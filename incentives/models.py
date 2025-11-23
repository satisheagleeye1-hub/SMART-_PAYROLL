from django.db import models
from django.utils import timezone
from accounts.models import Employee
from decimal import Decimal


class Person(models.Model):
    """Person/Client details who gives payment"""
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15, unique=True, db_index=True)
    location = models.CharField(max_length=100, blank=True)
    area = models.CharField(max_length=100, blank=True)
    mail_id = models.EmailField(max_length=100, blank=True)
    training_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Persons'
    
    def __str__(self):
        return f"{self.name} - {self.mobile}"


class DailyCollection(models.Model):
    """Daily collection records with automatic incentive calculation"""
    
    OFFICE_TYPE_CHOICES = [
        ('first', 'First Office'),
        ('second', 'Second Office'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='collections')
    person = models.ForeignKey(Person, on_delete=models.SET_NULL, null=True, blank=True, related_name='collections')
    date = models.DateField(default=timezone.now)
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    office_type = models.CharField(max_length=10, choices=OFFICE_TYPE_CHOICES, default='first')
    incentive_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payout_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Allow more than one collection row per employee per date (previously unique_together prevented duplicates)
        ordering = ['-date']
        verbose_name_plural = 'Daily Collections'
        indexes = [
            models.Index(fields=['employee', 'date']),
        ]

    def __str__(self):
        person_name = self.person.name if self.person else "N/A"
        return f"{self.employee.emp_id} - {self.date} - ₹{self.amount_collected} - {person_name}"
    
    def calculate_payout(self):
        """Calculate payout based on office type"""
        if self.amount_collected <= 0:
            self.payout_amount = Decimal('0.00')
            return
        
        if self.office_type == 'first':
            # First office: 85% of collected amount
            self.payout_amount = (self.amount_collected * Decimal('0.85')).quantize(Decimal('0.01'))
        elif self.office_type == 'second':
            # Second office: 85% of (half of collected amount)
            half_amount = self.amount_collected / Decimal('2.00')
            self.payout_amount = (half_amount * Decimal('0.85')).quantize(Decimal('0.01'))
        else:
            self.payout_amount = Decimal('0.00')
    
    def calculate_incentive(self):
        """
        Calculate incentive for this single record based on its own amount.
        (Primary group calculation is done in save() to combine multiple records on the same date.)
        For a single record: units = floor(amount / 1950), incentive = max(0, (units - 1) * 500)
        NOTE: Second office payments get NO incentive - only first office payments are eligible.
        """
        # Second office gets no incentive
        if self.office_type == 'second':
            self.incentive_earned = Decimal('0.00')
            return
        
        if self.amount_collected <= 0:
            self.incentive_earned = Decimal('0.00')
            return

        base_amount = Decimal('1950.00')
        incentive_per_unit = Decimal('500.00')

        units = int(self.amount_collected // base_amount)
        units = max(0, units)
        if units <= 1:
            self.incentive_earned = Decimal('0.00')
        else:
            self.incentive_earned = Decimal(units - 1) * incentive_per_unit

    def save(self, *args, **kwargs):
        """
        Save the instance, then recalculate incentive for the whole employee+date group.
        This ensures multiple collection rows on the same date combine to produce the correct incentive.
        The combined incentive is distributed as marginal incentives across rows ordered by creation time.
        Rule implemented: units = floor(total_collected / 1950); total_incentive = max(0, (units - 1) * 500)
        We'll compute marginal incentives per row so that the second unit yields 500, third yields 500, etc.
        """
        # Calculate payout before saving
        self.calculate_payout()
        
        # Save the instance first so it has a primary key
        super().save(*args, **kwargs)

        # Recalculate group total and distribute incentive per-row (no recursive save calls)
        # IMPORTANT: Only 'first' office type collections are eligible for incentives
        from django.db.models import Sum
        from django.db import transaction

        base_amount = Decimal('1950.00')
        incentive_per_unit = Decimal('500.00')

        # Fetch ALL rows for the employee/date ordered by creation time (oldest first)
        all_rows = list(DailyCollection.objects.filter(employee=self.employee, date=self.date).order_by('created_at', 'pk'))
        
        # Separate first office and second office rows
        first_office_rows = [row for row in all_rows if row.office_type == 'first']
        second_office_rows = [row for row in all_rows if row.office_type == 'second']

        # Set incentive to 0 for all second office rows
        with transaction.atomic():
            for row in second_office_rows:
                DailyCollection.objects.filter(pk=row.pk).update(incentive_earned=Decimal('0.00'))
            
            # Compute cumulative and assign marginal incentives ONLY for first office rows
            cumulative = Decimal('0.00')
            prev_total_incentive = Decimal('0.00')
            
            for row in first_office_rows:
                cumulative += Decimal(row.amount_collected)
                units = int(cumulative // base_amount) if cumulative > 0 else 0
                total_incentive_at_row = Decimal(units - 1) * incentive_per_unit if units > 1 else Decimal('0.00')
                marginal = total_incentive_at_row - prev_total_incentive
                # Ensure non-negative
                if marginal < 0:
                    marginal = Decimal('0.00')
                # Update the row's incentive_earned to the marginal contribution
                DailyCollection.objects.filter(pk=row.pk).update(incentive_earned=marginal)
                prev_total_incentive = total_incentive_at_row
