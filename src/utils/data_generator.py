"""
Mock Data Generator for InsightX Leadership Analytics.

Generates realistic synthetic payment transaction data with embedded
patterns and anomalies for demonstration purposes.
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

import numpy as np
import pandas as pd

# Optional: Use Faker if available, otherwise use hardcoded values
try:
    from faker import Faker
    FAKER_AVAILABLE = True
except ImportError:
    FAKER_AVAILABLE = False


class MockDataGenerator:
    """
    Generate synthetic payment transaction data with realistic patterns.
    
    This generator creates data that follows the InsightX hackathon schema
    and embeds specific patterns for demonstration:
    - Higher failure rates for Bill Payments on weekends
    - Fraud flags correlated with high-value transactions
    - Device-based amount variations
    
    Example:
        generator = MockDataGenerator(seed=42)
        df = generator.generate_data(num_rows=500)
        df.to_csv('data/transactions.csv', index=False)
    """
    
    # Configuration constants
    TRANSACTION_TYPES = ['P2P', 'P2M', 'Bill Payment', 'Recharge']
    TRANSACTION_TYPE_WEIGHTS = [0.35, 0.35, 0.20, 0.10]  # Distribution
    
    MERCHANT_CATEGORIES = ['Food', 'Grocery', 'Fuel', 'Entertainment', 'Utilities']
    MERCHANT_CATEGORY_BY_TYPE = {
        'P2M': ['Food', 'Grocery', 'Fuel', 'Entertainment'],
        'Bill Payment': ['Utilities'],
        'Recharge': ['Utilities']
    }
    
    AGE_GROUPS = ['18-25', '26-35', '36-45', '46-55', '56+']
    AGE_GROUP_WEIGHTS = [0.25, 0.35, 0.20, 0.12, 0.08]  # Younger skew
    
    INDIAN_STATES = [
        'Maharashtra', 'Karnataka', 'Tamil Nadu', 'Delhi', 'Gujarat',
        'Rajasthan', 'Uttar Pradesh', 'West Bengal', 'Telangana', 'Kerala'
    ]
    STATE_WEIGHTS = [0.18, 0.15, 0.12, 0.12, 0.10, 0.08, 0.08, 0.07, 0.06, 0.04]
    
    BANKS = ['SBI', 'HDFC', 'ICICI', 'Axis', 'Yes Bank']
    BANK_WEIGHTS = [0.30, 0.25, 0.20, 0.15, 0.10]
    
    DEVICE_TYPES = ['Android', 'iOS', 'Web']
    DEVICE_WEIGHTS = [0.60, 0.30, 0.10]
    
    NETWORK_TYPES = ['4G', '5G', 'WiFi']
    NETWORK_WEIGHTS = [0.50, 0.30, 0.20]
    
    # Amount ranges by device (for Insight 3: iOS has higher amounts)
    AMOUNT_RANGES = {
        'Android': (10.0, 25000.0),
        'iOS': (50.0, 45000.0),  # Higher floor and ceiling
        'Web': (100.0, 75000.0)  # Web typically for larger transactions
    }
    
    # Failure and fraud rates
    BASE_FAILURE_RATE = 0.05  # 5% baseline
    WEEKEND_BILLPAY_FAILURE_RATE = 0.20  # 20% for Bill Payment on weekends
    BASE_FRAUD_RATE = 0.02  # 2% baseline
    HIGH_VALUE_FRAUD_RATE = 0.10  # 10% for amounts > 50,000
    HIGH_VALUE_THRESHOLD = 50000.0
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize the data generator.
        
        Args:
            seed: Random seed for reproducibility. If None, results will vary.
        """
        self.seed = seed
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Initialize Faker if available
        if FAKER_AVAILABLE:
            self.faker = Faker('en_IN')
            if seed:
                Faker.seed(seed)
        else:
            self.faker = None
    
    def _generate_transaction_id(self) -> str:
        """Generate a unique transaction ID."""
        return f"TXN{uuid.uuid4().hex[:12].upper()}"
    
    def _generate_timestamp(self, days_back: int = 30) -> datetime:
        """
        Generate a random timestamp within the last N days.
        
        Args:
            days_back: Number of days to look back from now.
        
        Returns:
            Random datetime within the specified range.
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days_back)
        
        # Random seconds between start and end
        time_delta = end_date - start_date
        random_seconds = random.randint(0, int(time_delta.total_seconds()))
        
        return start_date + timedelta(seconds=random_seconds)
    
    def _generate_amount(self, device_type: str, transaction_type: str) -> float:
        """
        Generate transaction amount based on device type and transaction type.
        
        Implements Insight 3: iOS has higher average amounts.
        
        Args:
            device_type: The device type (Android, iOS, Web).
            transaction_type: The transaction type.
        
        Returns:
            Transaction amount in INR.
        """
        min_amt, max_amt = self.AMOUNT_RANGES.get(device_type, (10.0, 25000.0))
        
        # Adjust ranges based on transaction type
        if transaction_type == 'Recharge':
            min_amt = 10.0
            max_amt = min(max_amt, 2000.0)  # Recharges typically smaller
        elif transaction_type == 'Bill Payment':
            min_amt = 100.0
            max_amt = min(max_amt, 50000.0)
        elif transaction_type == 'P2P':
            # P2P can have wide range
            pass
        elif transaction_type == 'P2M':
            min_amt = 20.0
            max_amt = min(max_amt, 30000.0)
        
        # Use log-normal distribution for realistic amount distribution
        # (most transactions are small, few are large)
        mean = np.log((min_amt + max_amt) / 4)
        sigma = 1.0
        
        amount = np.random.lognormal(mean, sigma)
        amount = np.clip(amount, min_amt, max_amt)
        
        return round(amount, 2)
    
    def _determine_failure_status(
        self,
        transaction_type: str,
        is_weekend: bool
    ) -> str:
        """
        Determine transaction status (SUCCESS/FAILED).
        
        Implements Insight 1: Bill Payments have 20% failure rate on weekends.
        
        Args:
            transaction_type: The transaction type.
            is_weekend: Whether the transaction is on a weekend.
        
        Returns:
            'SUCCESS' or 'FAILED'.
        """
        # Insight 1: Higher failure rate for Bill Payment on weekends
        if transaction_type == 'Bill Payment' and is_weekend:
            failure_rate = self.WEEKEND_BILLPAY_FAILURE_RATE
        else:
            failure_rate = self.BASE_FAILURE_RATE
        
        return 'FAILED' if random.random() < failure_rate else 'SUCCESS'
    
    def _determine_fraud_flag(self, amount: float) -> int:
        """
        Determine fraud flag based on transaction amount.
        
        Implements Insight 2: High-value transactions (>50k) have 10% fraud flag rate.
        
        Args:
            amount: Transaction amount in INR.
        
        Returns:
            1 if flagged for review, 0 otherwise.
        """
        if amount > self.HIGH_VALUE_THRESHOLD:
            fraud_rate = self.HIGH_VALUE_FRAUD_RATE
        else:
            fraud_rate = self.BASE_FRAUD_RATE
        
        return 1 if random.random() < fraud_rate else 0
    
    def _weighted_choice(self, options: List[Any], weights: List[float]) -> Any:
        """Helper to make weighted random choices."""
        return random.choices(options, weights=weights, k=1)[0]
    
    def _get_merchant_category(self, transaction_type: str) -> Optional[str]:
        """
        Get merchant category based on transaction type.
        
        Implements Rule A & B: P2P has no merchant, others have valid categories.
        
        Args:
            transaction_type: The transaction type.
        
        Returns:
            Merchant category string or None for P2P.
        """
        if transaction_type == 'P2P':
            return None  # Rule A: P2P has no merchant
        
        # Rule B: Non-P2P has valid merchant category
        categories = self.MERCHANT_CATEGORY_BY_TYPE.get(
            transaction_type,
            self.MERCHANT_CATEGORIES
        )
        return random.choice(categories)
    
    def _get_receiver_age_group(self, transaction_type: str) -> Optional[str]:
        """
        Get receiver age group based on transaction type.
        
        Implements Rule A & B: P2P has receiver age, others don't.
        
        Args:
            transaction_type: The transaction type.
        
        Returns:
            Age group string or None for non-P2P.
        """
        if transaction_type == 'P2P':
            # Rule A: P2P has receiver age group
            return self._weighted_choice(self.AGE_GROUPS, self.AGE_GROUP_WEIGHTS)
        
        # Rule B: Non-P2P has no receiver age group
        return None
    
    def _calculate_derived_fields(self, timestamp: datetime) -> Dict[str, Any]:
        """
        Calculate derived fields from timestamp.
        
        Args:
            timestamp: The transaction timestamp.
        
        Returns:
            Dictionary with hour_of_day, day_of_week, is_weekend.
        """
        return {
            'hour_of_day': timestamp.hour,
            'day_of_week': timestamp.strftime('%A'),
            'is_weekend': 1 if timestamp.weekday() >= 5 else 0
        }
    
    def generate_single_transaction(self) -> Dict[str, Any]:
        """
        Generate a single transaction record.
        
        Returns:
            Dictionary containing all transaction fields.
        """
        # Generate base fields
        timestamp = self._generate_timestamp(days_back=30)
        transaction_type = self._weighted_choice(
            self.TRANSACTION_TYPES,
            self.TRANSACTION_TYPE_WEIGHTS
        )
        device_type = self._weighted_choice(self.DEVICE_TYPES, self.DEVICE_WEIGHTS)
        
        # Calculate derived fields early (needed for failure logic)
        derived = self._calculate_derived_fields(timestamp)
        is_weekend = derived['is_weekend'] == 1
        
        # Generate amount (Insight 3: iOS has higher amounts)
        amount = self._generate_amount(device_type, transaction_type)
        
        # Build transaction record
        transaction = {
            'transaction_id': self._generate_transaction_id(),
            'timestamp': timestamp,
            'transaction_type': transaction_type,
            'merchant_category': self._get_merchant_category(transaction_type),
            'amount_inr': amount,
            'transaction_status': self._determine_failure_status(
                transaction_type, is_weekend
            ),
            'sender_age_group': self._weighted_choice(
                self.AGE_GROUPS,
                self.AGE_GROUP_WEIGHTS
            ),
            'receiver_age_group': self._get_receiver_age_group(transaction_type),
            'sender_state': self._weighted_choice(
                self.INDIAN_STATES,
                self.STATE_WEIGHTS
            ),
            'sender_bank': self._weighted_choice(self.BANKS, self.BANK_WEIGHTS),
            'receiver_bank': self._weighted_choice(self.BANKS, self.BANK_WEIGHTS),
            'device_type': device_type,
            'network_type': self._weighted_choice(
                self.NETWORK_TYPES,
                self.NETWORK_WEIGHTS
            ),
            'fraud_flag': self._determine_fraud_flag(amount),
            **derived  # Add hour_of_day, day_of_week, is_weekend
        }
        
        return transaction
    
    def generate_data(self, num_rows: int = 500) -> pd.DataFrame:
        """
        Generate a complete synthetic dataset.
        
        Args:
            num_rows: Number of transaction records to generate.
        
        Returns:
            Pandas DataFrame with all transaction data.
        
        Example:
            generator = MockDataGenerator(seed=42)
            df = generator.generate_data(500)
            print(df.info())
        """
        transactions = [
            self.generate_single_transaction()
            for _ in range(num_rows)
        ]
        
        df = pd.DataFrame(transactions)
        
        # Sort by timestamp
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Ensure correct data types
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['amount_inr'] = df['amount_inr'].astype(float)
        df['fraud_flag'] = df['fraud_flag'].astype(int)
        df['is_weekend'] = df['is_weekend'].astype(int)
        df['hour_of_day'] = df['hour_of_day'].astype(int)
        
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        Generate a summary of the dataset for validation.
        
        Args:
            df: The generated DataFrame.
        
        Returns:
            Dictionary with summary statistics.
        """
        summary = {
            'total_records': len(df),
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat()
            },
            'transaction_type_distribution': df['transaction_type'].value_counts().to_dict(),
            'overall_failure_rate': (df['transaction_status'] == 'FAILED').mean(),
            'fraud_flag_rate': df['fraud_flag'].mean(),
            'avg_amount_by_device': df.groupby('device_type')['amount_inr'].mean().to_dict(),
            'weekend_billpay_failure_rate': None,
            'high_value_fraud_rate': None,
            'p2p_null_merchant_check': None,
            'non_p2p_null_receiver_age_check': None
        }
        
        # Insight 1 validation: Weekend Bill Payment failure rate
        weekend_billpay = df[
            (df['transaction_type'] == 'Bill Payment') &
            (df['is_weekend'] == 1)
        ]
        if len(weekend_billpay) > 0:
            summary['weekend_billpay_failure_rate'] = (
                weekend_billpay['transaction_status'] == 'FAILED'
            ).mean()
        
        # Insight 2 validation: High-value fraud rate
        high_value = df[df['amount_inr'] > self.HIGH_VALUE_THRESHOLD]
        if len(high_value) > 0:
            summary['high_value_fraud_rate'] = high_value['fraud_flag'].mean()
        
        # Rule A validation: P2P has null merchant_category
        p2p_records = df[df['transaction_type'] == 'P2P']
        summary['p2p_null_merchant_check'] = p2p_records['merchant_category'].isna().all()
        
        # Rule B validation: Non-P2P has null receiver_age_group
        non_p2p_records = df[df['transaction_type'] != 'P2P']
        summary['non_p2p_null_receiver_age_check'] = non_p2p_records['receiver_age_group'].isna().all()
        
        return summary
    
    def validate_data(self, df: pd.DataFrame) -> List[str]:
        """
        Validate the generated data against business rules.
        
        Args:
            df: The generated DataFrame.
        
        Returns:
            List of validation error messages (empty if all valid).
        """
        errors = []
        
        # Rule A: P2P must have null merchant_category
        p2p_with_merchant = df[
            (df['transaction_type'] == 'P2P') &
            (df['merchant_category'].notna())
        ]
        if len(p2p_with_merchant) > 0:
            errors.append(
                f"Rule A violated: {len(p2p_with_merchant)} P2P transactions "
                "have non-null merchant_category"
            )
        
        # Rule A: P2P must have valid receiver_age_group
        p2p_without_receiver = df[
            (df['transaction_type'] == 'P2P') &
            (df['receiver_age_group'].isna())
        ]
        if len(p2p_without_receiver) > 0:
            errors.append(
                f"Rule A violated: {len(p2p_without_receiver)} P2P transactions "
                "have null receiver_age_group"
            )
        
        # Rule B: Non-P2P must have null receiver_age_group
        non_p2p_types = ['P2M', 'Bill Payment', 'Recharge']
        non_p2p_with_receiver = df[
            (df['transaction_type'].isin(non_p2p_types)) &
            (df['receiver_age_group'].notna())
        ]
        if len(non_p2p_with_receiver) > 0:
            errors.append(
                f"Rule B violated: {len(non_p2p_with_receiver)} non-P2P transactions "
                "have non-null receiver_age_group"
            )
        
        # Rule B: Non-P2P must have valid merchant_category
        non_p2p_without_merchant = df[
            (df['transaction_type'].isin(non_p2p_types)) &
            (df['merchant_category'].isna())
        ]
        if len(non_p2p_without_merchant) > 0:
            errors.append(
                f"Rule B violated: {len(non_p2p_without_merchant)} non-P2P transactions "
                "have null merchant_category"
            )
        
        return errors


def generate_and_save_dataset(
    output_path: str = 'data/transactions.csv',
    num_rows: int = 500,
    seed: int = 42
) -> pd.DataFrame:
    """
    Convenience function to generate and save the dataset.
    
    Args:
        output_path: Path to save the CSV file.
        num_rows: Number of records to generate.
        seed: Random seed for reproducibility.
    
    Returns:
        The generated DataFrame.
    """
    generator = MockDataGenerator(seed=seed)
    df = generator.generate_data(num_rows=num_rows)
    
    # Validate
    errors = generator.validate_data(df)
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Data validation passed!")
    
    # Print summary
    summary = generator.get_data_summary(df)
    print(f"\nDataset Summary:")
    print(f"  Total records: {summary['total_records']}")
    print(f"  Date range: {summary['date_range']['start'][:10]} to {summary['date_range']['end'][:10]}")
    print(f"  Overall failure rate: {summary['overall_failure_rate']:.1%}")
    print(f"  Overall fraud flag rate: {summary['fraud_flag_rate']:.1%}")
    print(f"  Weekend Bill Payment failure rate: {summary['weekend_billpay_failure_rate']:.1%}")
    print(f"  High-value (>50k) fraud rate: {summary['high_value_fraud_rate']:.1%}")
    print(f"\n  Avg Amount by Device:")
    for device, avg in summary['avg_amount_by_device'].items():
        print(f"    {device}: INR {avg:,.2f}")
    
    # Save to CSV
    df.to_csv(output_path, index=False)
    print(f"\nDataset saved to: {output_path}")
    
    return df


# CLI Entry point
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate synthetic payment transaction data for InsightX'
    )
    parser.add_argument(
        '-n', '--num-rows',
        type=int,
        default=500,
        help='Number of records to generate (default: 500)'
    )
    parser.add_argument(
        '-o', '--output',
        type=str,
        default='data/transactions.csv',
        help='Output CSV file path (default: data/transactions.csv)'
    )
    parser.add_argument(
        '-s', '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    args = parser.parse_args()
    
    generate_and_save_dataset(
        output_path=args.output,
        num_rows=args.num_rows,
        seed=args.seed
    )
