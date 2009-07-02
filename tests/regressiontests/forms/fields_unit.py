# -*- coding: utf-8 -*-
import datetime
import time
import re
from unittest import TestCase
import os

from django.forms import *
from django.forms.widgets import RadioFieldRenderer
from django.core.files.uploadedfile import SimpleUploadedFile

try:
    from decimal import Decimal
except ImportError:
    from django.utils._decimal import Decimal

def fix_os_paths(x):
    if isinstance(x, basestring):
        return x.replace('\\', '/')
    elif isinstance(x, tuple):
        return tuple(fix_os_paths(list(x)))
    elif isinstance(x, list):
        return [fix_os_paths(y) for y in x]
    else:
        return x


class TestFields(TestCase):
    def assertRaisesErrorWithMessage(self, error, message, callable, *args, **kwargs):
        self.assertRaises(error, callable, *args, **kwargs)
        try:
            callable(*args, **kwargs)
        except error, e:
            self.assertEqual(message, str(e))

    # CharField ###################################################################

    def test_converted_0(self):
        f = CharField()
        self.assertEqual(u'1', f.clean(1))
        self.assertEqual(u'hello', f.clean('hello'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertEqual(u'[1, 2, 3]', f.clean([1, 2, 3]))

    def test_converted_1(self):
        f = CharField(required=False)
        self.assertEqual(u'1', f.clean(1))
        self.assertEqual(u'hello', f.clean('hello'))
        self.assertEqual(u'', f.clean(None))
        self.assertEqual(u'', f.clean(''))
        self.assertEqual(u'[1, 2, 3]', f.clean([1, 2, 3]))

    def test_converted_2(self):
        f = CharField(max_length=10, required=False)
        self.assertEqual(u'12345', f.clean('12345'))
        self.assertEqual(u'1234567890', f.clean('1234567890'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at most 10 characters (it has 11).']", f.clean, '1234567890a')

    def test_converted_3(self):
        f = CharField(min_length=10, required=False)
        self.assertEqual(u'', f.clean(''))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at least 10 characters (it has 5).']", f.clean, '12345')
        self.assertEqual(u'1234567890', f.clean('1234567890'))
        self.assertEqual(u'1234567890a', f.clean('1234567890a'))

    def test_converted_4(self):
        f = CharField(min_length=10, required=True)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at least 10 characters (it has 5).']", f.clean, '12345')
        self.assertEqual(u'1234567890', f.clean('1234567890'))
        self.assertEqual(u'1234567890a', f.clean('1234567890a'))

    # IntegerField ################################################################

    def test_converted_5(self):
        f = IntegerField()
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertEqual(1, f.clean('1'))
        self.assertEqual(True, isinstance(f.clean('1'), int))
        self.assertEqual(23, f.clean('23'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a whole number.']", f.clean, 'a')
        self.assertEqual(42, f.clean(42))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a whole number.']", f.clean, 3.14)
        self.assertEqual(1, f.clean('1 '))
        self.assertEqual(1, f.clean(' 1'))
        self.assertEqual(1, f.clean(' 1 '))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a whole number.']", f.clean, '1a')

    def test_converted_6(self):
        f = IntegerField(required=False)
        self.assertEqual(None, f.clean(''))
        self.assertEqual('None', repr(f.clean('')))
        self.assertEqual(None, f.clean(None))
        self.assertEqual('None', repr(f.clean(None)))
        self.assertEqual(1, f.clean('1'))
        self.assertEqual(True, isinstance(f.clean('1'), int))
        self.assertEqual(23, f.clean('23'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a whole number.']", f.clean, 'a')
        self.assertEqual(1, f.clean('1 '))
        self.assertEqual(1, f.clean(' 1'))
        self.assertEqual(1, f.clean(' 1 '))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a whole number.']", f.clean, '1a')

    def test_converted_7(self):
        f = IntegerField(max_value=10)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertEqual(1, f.clean(1))
        self.assertEqual(10, f.clean(10))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value is less than or equal to 10.']", f.clean, 11)
        self.assertEqual(10, f.clean('10'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value is less than or equal to 10.']", f.clean, '11')

    def test_converted_8(self):
        f = IntegerField(min_value=10)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value is greater than or equal to 10.']", f.clean, 1)
        self.assertEqual(10, f.clean(10))
        self.assertEqual(11, f.clean(11))
        self.assertEqual(10, f.clean('10'))
        self.assertEqual(11, f.clean('11'))

    def test_converted_9(self):
        f = IntegerField(min_value=10, max_value=20)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value is greater than or equal to 10.']", f.clean, 1)
        self.assertEqual(10, f.clean(10))
        self.assertEqual(11, f.clean(11))
        self.assertEqual(10, f.clean('10'))
        self.assertEqual(11, f.clean('11'))
        self.assertEqual(20, f.clean(20))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value is less than or equal to 20.']", f.clean, 21)

    # FloatField ##################################################################

    def test_converted_10(self):
        f = FloatField()
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertEqual(1.0, f.clean('1'))
        self.assertEqual(True, isinstance(f.clean('1'), float))
        self.assertEqual(23.0, f.clean('23'))
        self.assertEqual(3.1400000000000001, f.clean('3.14'))
        self.assertEqual(3.1400000000000001, f.clean(3.14))
        self.assertEqual(42.0, f.clean(42))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a number.']", f.clean, 'a')
        self.assertEqual(1.0, f.clean('1.0 '))
        self.assertEqual(1.0, f.clean(' 1.0'))
        self.assertEqual(1.0, f.clean(' 1.0 '))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a number.']", f.clean, '1.0a')

    def test_converted_11(self):
        f = FloatField(required=False)
        self.assertEqual(None, f.clean(''))
        self.assertEqual(None, f.clean(None))
        self.assertEqual(1.0, f.clean('1'))

    def test_converted_12(self):
        f = FloatField(max_value=1.5, min_value=0.5)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value is less than or equal to 1.5.']", f.clean, '1.6')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value is greater than or equal to 0.5.']", f.clean, '0.4')
        self.assertEqual(1.5, f.clean('1.5'))
        self.assertEqual(0.5, f.clean('0.5'))
    
    # DecimalField ################################################################

    def test_converted_13(self):
        f = DecimalField(max_digits=4, decimal_places=2)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertEqual(True, f.clean('1') == Decimal("1"))
        self.assertEqual(True, isinstance(f.clean('1'), Decimal))
        self.assertEqual(True, f.clean('23') == Decimal("23"))
        self.assertEqual(True, f.clean('3.14') == Decimal("3.14"))
        self.assertEqual(True, f.clean(3.14) == Decimal("3.14"))
        self.assertEqual(True, f.clean(Decimal('3.14')) == Decimal("3.14"))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a number.']", f.clean, 'a')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a number.']", f.clean, u'łąść')
        self.assertEqual(True, f.clean('1.0 ') == Decimal("1.0"))
        self.assertEqual(True, f.clean(' 1.0') == Decimal("1.0"))
        self.assertEqual(True, f.clean(' 1.0 ') == Decimal("1.0"))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a number.']", f.clean, '1.0a')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure that there are no more than 4 digits in total.']", f.clean, '123.45')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure that there are no more than 2 decimal places.']", f.clean, '1.234')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure that there are no more than 2 digits before the decimal point.']", f.clean, '123.4')
        self.assertEqual(True, f.clean('-12.34') == Decimal("-12.34"))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure that there are no more than 4 digits in total.']", f.clean, '-123.45')
        self.assertEqual(True, f.clean('-.12') == Decimal("-0.12"))
        self.assertEqual(True, f.clean('-00.12') == Decimal("-0.12"))
        self.assertEqual(True, f.clean('-000.12') == Decimal("-0.12"))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure that there are no more than 2 decimal places.']", f.clean, '-000.123')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure that there are no more than 4 digits in total.']", f.clean, '-000.12345')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a number.']", f.clean, '--0.12')

    def test_converted_14(self):
        f = DecimalField(max_digits=4, decimal_places=2, required=False)
        self.assertEqual(None, f.clean(''))
        self.assertEqual(None, f.clean(None))
        self.assertEqual(True, f.clean('1') == Decimal("1"))

    def test_converted_15(self):
        f = DecimalField(max_digits=4, decimal_places=2, max_value=Decimal('1.5'), min_value=Decimal('0.5'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value is less than or equal to 1.5.']", f.clean, '1.6')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value is greater than or equal to 0.5.']", f.clean, '0.4')
        self.assertEqual(True, f.clean('1.5') == Decimal("1.5"))
        self.assertEqual(True, f.clean('0.5') == Decimal("0.5"))
        self.assertEqual(True, f.clean('.5') == Decimal("0.5"))
        self.assertEqual(True, f.clean('00.50') == Decimal("0.50"))

    def test_converted_16(self):
        f = DecimalField(decimal_places=2)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure that there are no more than 2 decimal places.']", f.clean, '0.00000001')

    def test_converted_17(self):
        f = DecimalField(max_digits=3)
        # Leading whole zeros "collapse" to one digit.
        self.assertEqual(True, f.clean('0000000.10') == Decimal("0.1"))
        # But a leading 0 before the . doesn't count towards max_digits
        self.assertEqual(True, f.clean('0000000.100') == Decimal("0.100"))
        # Only leading whole zeros "collapse" to one digit.
        self.assertEqual(True, f.clean('000000.02') == Decimal('0.02'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure that there are no more than 3 digits in total.']", f.clean, '000000.0002')
        self.assertEqual(True, f.clean('.002') == Decimal("0.002"))

    def test_converted_18(self):
        f = DecimalField(max_digits=2, decimal_places=2)
        self.assertEqual(True, f.clean('.01') == Decimal(".01"))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure that there are no more than 0 digits before the decimal point.']", f.clean, '1.1')

    # DateField ###################################################################

    def test_converted_19(self):
        f = DateField()
        self.assertEqual(datetime.date(2006, 10, 25), f.clean(datetime.date(2006, 10, 25)))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean(datetime.datetime(2006, 10, 25, 14, 30)))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59)))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59, 200)))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean('2006-10-25'))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean('10/25/2006'))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean('10/25/06'))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean('Oct 25 2006'))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean('October 25 2006'))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean('October 25, 2006'))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean('25 October 2006'))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean('25 October, 2006'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.']", f.clean, '2006-4-31')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.']", f.clean, '200a-10-25')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.']", f.clean, '25/10/06')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)

    def test_converted_20(self):
        f = DateField(required=False)
        self.assertEqual(None, f.clean(None))
        self.assertEqual('None', repr(f.clean(None)))
        self.assertEqual(None, f.clean(''))
        self.assertEqual('None', repr(f.clean('')))

    def test_converted_21(self):
        f = DateField(input_formats=['%Y %m %d'])
        self.assertEqual(datetime.date(2006, 10, 25), f.clean(datetime.date(2006, 10, 25)))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean(datetime.datetime(2006, 10, 25, 14, 30)))
        self.assertEqual(datetime.date(2006, 10, 25), f.clean('2006 10 25'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.']", f.clean, '2006-10-25')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.']", f.clean, '10/25/2006')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.']", f.clean, '10/25/06')

    # TimeField ###################################################################

    def test_converted_22(self):
        f = TimeField()
        self.assertEqual(datetime.time(14, 25), f.clean(datetime.time(14, 25)))
        self.assertEqual(datetime.time(14, 25, 59), f.clean(datetime.time(14, 25, 59)))
        self.assertEqual(datetime.time(14, 25), f.clean('14:25'))
        self.assertEqual(datetime.time(14, 25, 59), f.clean('14:25:59'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid time.']", f.clean, 'hello')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid time.']", f.clean, '1:24 p.m.')

    def test_converted_23(self):
        f = TimeField(input_formats=['%I:%M %p'])
        self.assertEqual(datetime.time(14, 25), f.clean(datetime.time(14, 25)))
        self.assertEqual(datetime.time(14, 25, 59), f.clean(datetime.time(14, 25, 59)))
        self.assertEqual(datetime.time(4, 25), f.clean('4:25 AM'))
        self.assertEqual(datetime.time(16, 25), f.clean('4:25 PM'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid time.']", f.clean, '14:30:45')

    # DateTimeField ###############################################################

    def test_converted_24(self):
        f = DateTimeField()
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean(datetime.date(2006, 10, 25)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean(datetime.datetime(2006, 10, 25, 14, 30)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 59), f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 59, 200), f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59, 200)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45), f.clean('2006-10-25 14:30:45'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('2006-10-25 14:30:00'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('2006-10-25 14:30'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean('2006-10-25'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45), f.clean('10/25/2006 14:30:45'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('10/25/2006 14:30:00'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('10/25/2006 14:30'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean('10/25/2006'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 45), f.clean('10/25/06 14:30:45'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('10/25/06 14:30:00'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('10/25/06 14:30'))
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean('10/25/06'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date/time.']", f.clean, 'hello')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date/time.']", f.clean, '2006-10-25 4:30 p.m.')

    def test_converted_25(self):
        f = DateTimeField(input_formats=['%Y %m %d %I:%M %p'])
        self.assertEqual(datetime.datetime(2006, 10, 25, 0, 0), f.clean(datetime.date(2006, 10, 25)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean(datetime.datetime(2006, 10, 25, 14, 30)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 59), f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30, 59, 200), f.clean(datetime.datetime(2006, 10, 25, 14, 30, 59, 200)))
        self.assertEqual(datetime.datetime(2006, 10, 25, 14, 30), f.clean('2006 10 25 2:30 PM'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date/time.']", f.clean, '2006-10-25 14:30:45')

    def test_converted_26(self):
        f = DateTimeField(required=False)
        self.assertEqual(None, f.clean(None))
        self.assertEqual('None', repr(f.clean(None)))
        self.assertEqual(None, f.clean(''))
        self.assertEqual('None', repr(f.clean('')))

    # RegexField ##################################################################

    def test_converted_27(self):
        f = RegexField('^\d[A-F]\d$')
        self.assertEqual(u'2A2', f.clean('2A2'))
        self.assertEqual(u'3F3', f.clean('3F3'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid value.']", f.clean, '3G3')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid value.']", f.clean, ' 2A2')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid value.']", f.clean, '2A2 ')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')

    def test_converted_28(self):
        f = RegexField('^\d[A-F]\d$', required=False)
        self.assertEqual(u'2A2', f.clean('2A2'))
        self.assertEqual(u'3F3', f.clean('3F3'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid value.']", f.clean, '3G3')
        self.assertEqual(u'', f.clean(''))

    def test_converted_29(self):
        f = RegexField(re.compile('^\d[A-F]\d$'))
        self.assertEqual(u'2A2', f.clean('2A2'))
        self.assertEqual(u'3F3', f.clean('3F3'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid value.']", f.clean, '3G3')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid value.']", f.clean, ' 2A2')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid value.']", f.clean, '2A2 ')

    def test_converted_30(self):
        f = RegexField('^\d\d\d\d$', error_message='Enter a four-digit number.')
        self.assertEqual(u'1234', f.clean('1234'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a four-digit number.']", f.clean, '123')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a four-digit number.']", f.clean, 'abcd')

    def test_converted_31(self):
        f = RegexField('^\d+$', min_length=5, max_length=10)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at least 5 characters (it has 3).']", f.clean, '123')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at least 5 characters (it has 3).']", f.clean, 'abc')
        self.assertEqual(u'12345', f.clean('12345'))
        self.assertEqual(u'1234567890', f.clean('1234567890'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at most 10 characters (it has 11).']", f.clean, '12345678901')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid value.']", f.clean, '12345a')

    # EmailField ##################################################################

    def test_converted_32(self):
        f = EmailField()
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertEqual(u'person@example.com', f.clean('person@example.com'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'foo')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'foo@')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'foo@bar')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'example@invalid-.com')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'example@-invalid.com')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'example@inv-.alid-.com')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'example@inv-.-alid.com')
        self.assertEqual(u'example@valid-----hyphens.com', f.clean('example@valid-----hyphens.com'))
        self.assertEqual(u'example@valid-with-hyphens.com', f.clean('example@valid-with-hyphens.com'))

    def test_converted_33(self):
        f = EmailField(required=False)
        self.assertEqual(u'', f.clean(''))
        self.assertEqual(u'', f.clean(None))
        self.assertEqual(u'person@example.com', f.clean('person@example.com'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'foo')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'foo@')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'foo@bar')

    def test_converted_34(self):
        f = EmailField(min_length=10, max_length=15)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at least 10 characters (it has 9).']", f.clean, 'a@foo.com')
        self.assertEqual(u'alf@foo.com', f.clean('alf@foo.com'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at most 15 characters (it has 20).']", f.clean, 'alf123456788@foo.com')

    # FileField ##################################################################

    def test_converted_35(self):
        f = FileField()
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '', '')
        self.assertEqual('files/test1.pdf', f.clean('', 'files/test1.pdf'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None, '')
        self.assertEqual('files/test2.pdf', f.clean(None, 'files/test2.pdf'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'No file was submitted. Check the encoding type on the form.']", f.clean, SimpleUploadedFile('', ''))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'No file was submitted. Check the encoding type on the form.']", f.clean, SimpleUploadedFile('', ''), '')
        self.assertEqual('files/test3.pdf', f.clean(None, 'files/test3.pdf'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'No file was submitted. Check the encoding type on the form.']", f.clean, 'some content that is not a file')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'The submitted file is empty.']", f.clean, SimpleUploadedFile('name', None))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'The submitted file is empty.']", f.clean, SimpleUploadedFile('name', ''))
        self.assertEqual(SimpleUploadedFile, type(f.clean(SimpleUploadedFile('name', 'Some File Content'))))
        self.assertEqual(SimpleUploadedFile, type(f.clean(SimpleUploadedFile('我隻氣墊船裝滿晒鱔.txt', 'मेरी मँडराने वाली नाव सर्पमीनों से भरी ह'))))
        self.assertEqual(SimpleUploadedFile, type(f.clean(SimpleUploadedFile('name', 'Some File Content'), 'files/test4.pdf')))

    def test_converted_36(self):
        f = FileField(max_length = 5)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this filename has at most 5 characters (it has 18).']", f.clean, SimpleUploadedFile('test_maxlength.txt', 'hello world'))
        self.assertEqual('files/test1.pdf', f.clean('', 'files/test1.pdf'))
        self.assertEqual('files/test2.pdf', f.clean(None, 'files/test2.pdf'))
        self.assertEqual(SimpleUploadedFile, type(f.clean(SimpleUploadedFile('name', 'Some File Content'))))

    # URLField ##################################################################

    def test_converted_37(self):
        f = URLField()
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertEqual(u'http://localhost/', f.clean('http://localhost'))
        self.assertEqual(u'http://example.com/', f.clean('http://example.com'))
        self.assertEqual(u'http://www.example.com/', f.clean('http://www.example.com'))
        self.assertEqual(u'http://www.example.com:8000/test', f.clean('http://www.example.com:8000/test'))
        self.assertEqual(u'http://valid-with-hyphens.com/', f.clean('valid-with-hyphens.com'))
        self.assertEqual(u'http://subdomain.domain.com/', f.clean('subdomain.domain.com'))
        self.assertEqual(u'http://200.8.9.10/', f.clean('http://200.8.9.10'))
        self.assertEqual(u'http://200.8.9.10:8000/test', f.clean('http://200.8.9.10:8000/test'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'foo')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://example')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://example.')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://.com')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://invalid-.com')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://-invalid.com')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://inv-.alid-.com')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://inv-.-alid.com')
        self.assertEqual(u'http://valid-----hyphens.com/', f.clean('http://valid-----hyphens.com'))

    def test_converted_38(self):
        f = URLField(required=False)
        self.assertEqual(u'', f.clean(''))
        self.assertEqual(u'', f.clean(None))
        self.assertEqual(u'http://example.com/', f.clean('http://example.com'))
        self.assertEqual(u'http://www.example.com/', f.clean('http://www.example.com'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'foo')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://example')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://example.')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://.com')

    def test_converted_39(self):
        f = URLField(verify_exists=True)
        self.assertEqual(u'http://www.google.com/', f.clean('http://www.google.com')) # This will fail if there's no Internet connection
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid URL.']", f.clean, 'http://example')
        self.assertRaises(ValidationError, f.clean, 'http://www.broken.djangoproject.com') # bad domain
        try:
            f.clean('http://www.broken.djangoproject.com') # bad domain
        except ValidationError, e:
            self.assertEqual("[u'This URL appears to be a broken link.']", str(e))
        self.assertRaises(ValidationError, f.clean, 'http://google.com/we-love-microsoft.html') # good domain, bad page
        try:
            f.clean('http://google.com/we-love-microsoft.html') # good domain, bad page
        except ValidationError, e:
            self.assertEqual("[u'This URL appears to be a broken link.']", str(e))

    def test_converted_40(self):
        f = URLField(verify_exists=True, required=False)
        self.assertEqual(u'', f.clean(''))
        self.assertEqual(u'http://www.google.com/', f.clean('http://www.google.com')) # This will fail if there's no Internet connection

    def test_converted_41(self):
        f = URLField(min_length=15, max_length=20)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at least 15 characters (it has 13).']", f.clean, 'http://f.com')
        self.assertEqual(u'http://example.com/', f.clean('http://example.com'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at most 20 characters (it has 38).']", f.clean, 'http://abcdefghijklmnopqrstuvwxyz.com')

    def test_converted_42(self):
        f = URLField(required=False)
        self.assertEqual(u'http://example.com/', f.clean('example.com'))
        self.assertEqual(u'', f.clean(''))
        self.assertEqual(u'https://example.com/', f.clean('https://example.com'))

    def test_converted_43(self):
        f = URLField()
        self.assertEqual(u'http://example.com/', f.clean('http://example.com'))
        self.assertEqual(u'http://example.com/test', f.clean('http://example.com/test'))
        
    # BooleanField ################################################################

    def test_converted_44(self):
        f = BooleanField()
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertEqual(True, f.clean(True))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, False)
        self.assertEqual(True, f.clean(1))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, 0)
        self.assertEqual(True, f.clean('Django rocks'))
        self.assertEqual(True, f.clean('True'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, 'False')

    def test_converted_45(self):
        f = BooleanField(required=False)
        self.assertEqual(False, f.clean(''))
        self.assertEqual(False, f.clean(None))
        self.assertEqual(True, f.clean(True))
        self.assertEqual(False, f.clean(False))
        self.assertEqual(True, f.clean(1))
        self.assertEqual(False, f.clean(0))
        self.assertEqual(True, f.clean('1'))
        self.assertEqual(False, f.clean('0'))
        self.assertEqual(True, f.clean('Django rocks'))
        self.assertEqual(False, f.clean('False'))
        
    # ChoiceField #################################################################

    def test_converted_46(self):
        f = ChoiceField(choices=[('1', 'One'), ('2', 'Two')])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertEqual(u'1', f.clean(1))
        self.assertEqual(u'1', f.clean('1'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. 3 is not one of the available choices.']", f.clean, '3')

    def test_converted_47(self):
        f = ChoiceField(choices=[('1', 'One'), ('2', 'Two')], required=False)
        self.assertEqual(u'', f.clean(''))
        self.assertEqual(u'', f.clean(None))
        self.assertEqual(u'1', f.clean(1))
        self.assertEqual(u'1', f.clean('1'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. 3 is not one of the available choices.']", f.clean, '3')

    def test_converted_48(self):
        f = ChoiceField(choices=[('J', 'John'), ('P', 'Paul')])
        self.assertEqual(u'J', f.clean('J'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. John is not one of the available choices.']", f.clean, 'John')

    def test_converted_49(self):
        f = ChoiceField(choices=[('Numbers', (('1', 'One'), ('2', 'Two'))), ('Letters', (('3','A'),('4','B'))), ('5','Other')])
        self.assertEqual(u'1', f.clean(1))
        self.assertEqual(u'1', f.clean('1'))
        self.assertEqual(u'3', f.clean(3))
        self.assertEqual(u'3', f.clean('3'))
        self.assertEqual(u'5', f.clean(5))
        self.assertEqual(u'5', f.clean('5'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. 6 is not one of the available choices.']", f.clean, '6')

    # TypedChoiceField ############################################################
    # TypedChoiceField is just like ChoiceField, except that coerced types will
    # be returned:

    def test_converted_50(self):
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int)
        self.assertEqual(1, f.clean('1'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. 2 is not one of the available choices.']", f.clean, '2')

    def test_converted_51(self):
        # Different coercion, same validation.
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=float)
        self.assertEqual(1.0, f.clean('1'))

    def test_converted_52(self):
        # This can also cause weirdness: be careful (bool(-1) == True, remember)
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=bool)
        self.assertEqual(True, f.clean('-1'))

    def test_converted_53(self):
        # Even more weirdness: if you have a valid choice but your coercion function
        # can't coerce, you'll still get a validation error. Don't do this!
        f = TypedChoiceField(choices=[('A', 'A'), ('B', 'B')], coerce=int)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. B is not one of the available choices.']", f.clean, 'B')
        # Required fields require values
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')

    def test_converted_54(self):
        # Non-required fields aren't required
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False)
        self.assertEqual('', f.clean(''))
        # If you want cleaning an empty value to return a different type, tell the field

    def test_converted_55(self):
        f = TypedChoiceField(choices=[(1, "+1"), (-1, "-1")], coerce=int, required=False, empty_value=None)
        self.assertEqual(None, f.clean(''))

    # NullBooleanField ############################################################

    def test_converted_56(self):
        f = NullBooleanField()
        self.assertEqual(None, f.clean(''))
        self.assertEqual(True, f.clean(True))
        self.assertEqual(False, f.clean(False))
        self.assertEqual(None, f.clean(None))
        self.assertEqual(False, f.clean('0'))
        self.assertEqual(True, f.clean('1'))
        self.assertEqual(None, f.clean('2'))
        self.assertEqual(None, f.clean('3'))
        self.assertEqual(None, f.clean('hello'))


    def test_converted_57(self):
        # Make sure that the internal value is preserved if using HiddenInput (#7753)
        class HiddenNullBooleanForm(Form):
            hidden_nullbool1 = NullBooleanField(widget=HiddenInput, initial=True)
            hidden_nullbool2 = NullBooleanField(widget=HiddenInput, initial=False)
        f = HiddenNullBooleanForm()
        self.assertEqual('<input type="hidden" name="hidden_nullbool1" value="True" id="id_hidden_nullbool1" /><input type="hidden" name="hidden_nullbool2" value="False" id="id_hidden_nullbool2" />', str(f))

    def test_converted_58(self):
        class HiddenNullBooleanForm(Form):
            hidden_nullbool1 = NullBooleanField(widget=HiddenInput, initial=True)
            hidden_nullbool2 = NullBooleanField(widget=HiddenInput, initial=False)
        f = HiddenNullBooleanForm({ 'hidden_nullbool1': 'True', 'hidden_nullbool2': 'False' })
        self.assertEqual(None, f.full_clean())
        self.assertEqual(True, f.cleaned_data['hidden_nullbool1'])
        self.assertEqual(False, f.cleaned_data['hidden_nullbool2'])

    def test_converted_59(self):
        # Make sure we're compatible with MySQL, which uses 0 and 1 for its boolean
        # values. (#9609)
        NULLBOOL_CHOICES = (('1', 'Yes'), ('0', 'No'), ('', 'Unknown'))
        class MySQLNullBooleanForm(Form):
            nullbool0 = NullBooleanField(widget=RadioSelect(choices=NULLBOOL_CHOICES))
            nullbool1 = NullBooleanField(widget=RadioSelect(choices=NULLBOOL_CHOICES))
            nullbool2 = NullBooleanField(widget=RadioSelect(choices=NULLBOOL_CHOICES))
        f = MySQLNullBooleanForm({ 'nullbool0': '1', 'nullbool1': '0', 'nullbool2': '' })
        self.assertEqual(None, f.full_clean())
        self.assertEqual(True, f.cleaned_data['nullbool0'])
        self.assertEqual(False, f.cleaned_data['nullbool1'])
        self.assertEqual(None, f.cleaned_data['nullbool2'])

    # MultipleChoiceField #########################################################

    def test_converted_60(self):
        f = MultipleChoiceField(choices=[('1', 'One'), ('2', 'Two')])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertEqual([u'1'], f.clean([1]))
        self.assertEqual([u'1'], f.clean(['1']))
        self.assertEqual([u'1', u'2'], f.clean(['1', '2']))
        self.assertEqual([u'1', u'2'], f.clean([1, '2']))
        self.assertEqual([u'1', u'2'], f.clean((1, '2')))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a list of values.']", f.clean, 'hello')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, [])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, ())
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. 3 is not one of the available choices.']", f.clean, ['3'])

    def test_converted_61(self):
        f = MultipleChoiceField(choices=[('1', 'One'), ('2', 'Two')], required=False)
        self.assertEqual([], f.clean(''))
        self.assertEqual([], f.clean(None))
        self.assertEqual([u'1'], f.clean([1]))
        self.assertEqual([u'1'], f.clean(['1']))
        self.assertEqual([u'1', u'2'], f.clean(['1', '2']))
        self.assertEqual([u'1', u'2'], f.clean([1, '2']))
        self.assertEqual([u'1', u'2'], f.clean((1, '2')))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a list of values.']", f.clean, 'hello')
        self.assertEqual([], f.clean([]))
        self.assertEqual([], f.clean(()))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. 3 is not one of the available choices.']", f.clean, ['3'])

    def test_converted_62(self):
        f = MultipleChoiceField(choices=[('Numbers', (('1', 'One'), ('2', 'Two'))), ('Letters', (('3','A'),('4','B'))), ('5','Other')])
        self.assertEqual([u'1'], f.clean([1]))
        self.assertEqual([u'1'], f.clean(['1']))
        self.assertEqual([u'1', u'5'], f.clean([1, 5]))
        self.assertEqual([u'1', u'5'], f.clean([1, '5']))
        self.assertEqual([u'1', u'5'], f.clean(['1', 5]))
        self.assertEqual([u'1', u'5'], f.clean(['1', '5']))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. 6 is not one of the available choices.']", f.clean, ['6'])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. 6 is not one of the available choices.']", f.clean, ['1','6'])

    # ComboField ##################################################################

    def test_converted_63(self):
        f = ComboField(fields=[CharField(max_length=20), EmailField()])
        self.assertEqual(u'test@example.com', f.clean('test@example.com'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at most 20 characters (it has 28).']", f.clean, 'longemailaddress@example.com')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'not an e-mail')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)

    def test_converted_64(self):
        f = ComboField(fields=[CharField(max_length=20), EmailField()], required=False)
        self.assertEqual(u'test@example.com', f.clean('test@example.com'))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Ensure this value has at most 20 characters (it has 28).']", f.clean, 'longemailaddress@example.com')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid e-mail address.']", f.clean, 'not an e-mail')
        self.assertEqual(u'', f.clean(''))
        self.assertEqual(u'', f.clean(None))
    
    # FilePathField ###############################################################

    def test_converted_65(self):
        path = forms.__file__
        path = os.path.dirname(path) + '/'
        assert fix_os_paths(path).endswith('/django/forms/')

    def test_converted_66(self):
        path = forms.__file__
        path = os.path.dirname(path) + '/'
        f = FilePathField(path=path)
        f.choices = [p for p in f.choices if p[0].endswith('.py')]
        f.choices.sort()
        expected = [
                ('/django/forms/__init__.py', '__init__.py'),
                ('/django/forms/fields.py', 'fields.py'),
                ('/django/forms/forms.py', 'forms.py'),
                ('/django/forms/formsets.py', 'formsets.py'),
                ('/django/forms/models.py', 'models.py'),
                ('/django/forms/util.py', 'util.py'),
                ('/django/forms/widgets.py', 'widgets.py')
            ]
        for exp, got in zip(expected, fix_os_paths(f.choices)):
            self.assertEqual(exp[1], got[1])
            assert got[0].endswith(exp[0])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Select a valid choice. fields.py is not one of the available choices.']", f.clean, 'fields.py')
        assert fix_os_paths(f.clean(path + 'fields.py')).endswith('/django/forms/fields.py')

    def test_converted_67(self):
        path = forms.__file__
        path = os.path.dirname(path) + '/'
        f = FilePathField(path=path, match='^.*?\.py$')
        f.choices.sort()
        expected = [
                ('/django/forms/__init__.py', '__init__.py'),
                ('/django/forms/fields.py', 'fields.py'),
                ('/django/forms/forms.py', 'forms.py'),
                ('/django/forms/formsets.py', 'formsets.py'),
                ('/django/forms/models.py', 'models.py'),
                ('/django/forms/util.py', 'util.py'),
                ('/django/forms/widgets.py', 'widgets.py')
            ]
        for exp, got in zip(expected, fix_os_paths(f.choices)):
            self.assertEqual(exp[1], got[1])
            assert got[0].endswith(exp[0])

    def test_converted_68(self):
        path = forms.__file__
        path = os.path.dirname(path) + '/'
        f = FilePathField(path=path, recursive=True, match='^.*?\.py$')
        f.choices.sort()
        expected = [
                ('/django/forms/__init__.py', '__init__.py'),
                ('/django/forms/extras/__init__.py', 'extras/__init__.py'),
                ('/django/forms/extras/widgets.py', 'extras/widgets.py'),
                ('/django/forms/fields.py', 'fields.py'),
                ('/django/forms/forms.py', 'forms.py'),
                ('/django/forms/formsets.py', 'formsets.py'),
                ('/django/forms/models.py', 'models.py'),
                ('/django/forms/util.py', 'util.py'),
                ('/django/forms/widgets.py', 'widgets.py')
            ]
        for exp, got in zip(expected, fix_os_paths(f.choices)):
            self.assertEqual(exp[1], got[1])
            assert got[0].endswith(exp[0])

    # SplitDateTimeField ##########################################################

    def test_converted_69(self):
        from django.forms.widgets import SplitDateTimeWidget
        f = SplitDateTimeField()
        assert isinstance(f.widget, SplitDateTimeWidget)
        self.assertEqual(datetime.datetime(2006, 1, 10, 7, 30), f.clean([datetime.date(2006, 1, 10), datetime.time(7, 30)]))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, None)
        self.assertRaisesErrorWithMessage(ValidationError, "[u'This field is required.']", f.clean, '')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a list of values.']", f.clean, 'hello')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.', u'Enter a valid time.']", f.clean, ['hello', 'there'])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid time.']", f.clean, ['2006-01-10', 'there'])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.']", f.clean, ['hello', '07:30'])

    def test_converted_70(self):
        f = SplitDateTimeField(required=False)
        self.assertEqual(datetime.datetime(2006, 1, 10, 7, 30), f.clean([datetime.date(2006, 1, 10), datetime.time(7, 30)]))
        self.assertEqual(datetime.datetime(2006, 1, 10, 7, 30), f.clean(['2006-01-10', '07:30']))
        self.assertEqual(None, f.clean(None))
        self.assertEqual(None, f.clean(''))
        self.assertEqual(None, f.clean(['']))
        self.assertEqual(None, f.clean(['', '']))
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a list of values.']", f.clean, 'hello')
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.', u'Enter a valid time.']", f.clean, ['hello', 'there'])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid time.']", f.clean, ['2006-01-10', 'there'])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.']", f.clean, ['hello', '07:30'])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid time.']", f.clean, ['2006-01-10', ''])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid time.']", f.clean, ['2006-01-10'])
        self.assertRaisesErrorWithMessage(ValidationError, "[u'Enter a valid date.']", f.clean, ['', '07:30'])
