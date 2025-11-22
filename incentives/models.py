from django.db import models
from django.utils import timezone
from accounts.models import Employee
from decimal import Decimal


class DailyCollection(models.Model):
    """Daily collection records with automatic incentive calculation"""
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='collections')
    date = models.DateField(default=timezone.now)
    amount_collected = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    incentive_earned = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
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
        return f"{self.employee.emp_id} - {self.date} - ₹{self.amount_collected}"
    
    def calculate_incentive(self):
        """
        Calculate incentive for this single record based on its own amount.
        (Primary group calculation is done in save() to combine multiple records on the same date.)
        For a single record: units = floor(amount / 1950), incentive = max(0, (units - 1) * 500)
        """
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
        # Save the instance first so it has a primary key
        super().save(*args, **kwargs)

        # Recalculate group total and distribute incentive per-row (no recursive save calls)
        from django.db.models import Sum
        from django.db import transaction

        base_amount = Decimal('1950.00')
        incentive_per_unit = Decimal('500.00')

        # Fetch rows for the employee/date ordered by creation time (oldest first)
        rows = list(DailyCollection.objects.filter(employee=self.employee, date=self.date).order_by('created_at', 'pk'))

        # Compute cumulative and assign marginal incentives
        cumulative = Decimal('0.00')
        prev_total_incentive = Decimal('0.00')

        with transaction.atomic():
            for row in rows:
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
