"""
The latest version of this package is available at:
<http://github.com/jantman/biweeklybudget>

################################################################################
Copyright 2016 Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>

    This file is part of biweeklybudget, also known as biweeklybudget.

    biweeklybudget is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    biweeklybudget is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with biweeklybudget.  If not, see <http://www.gnu.org/licenses/>.

The Copyright and Authors attributions contained herein may not be removed or
otherwise altered, except to add the Author attribution of a contributor to
this work. (Additional Terms pursuant to Section 7b of the AGPL v3)
################################################################################
While not legally required, I sincerely request that anyone who finds
bugs please submit them at <https://github.com/jantman/biweeklybudget> or
to me via email, and that you send any contributions or improvements
either as a pull request on GitHub, or to me ia email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

import pytest
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from pytz import UTC
from selenium.webdriver.support.ui import Select

from biweeklybudget.utils import dtnow
from biweeklybudget.tests.acceptance_helpers import AcceptanceHelper
from biweeklybudget.settings import PAY_PERIOD_START_DATE
from biweeklybudget.biweeklypayperiod import BiweeklyPayPeriod
from biweeklybudget.models import *
import biweeklybudget.models.base  # noqa
from biweeklybudget.tests.conftest import engine

dt = dtnow()


@pytest.mark.acceptance
class DONOTTestPayPeriods(AcceptanceHelper):

    @pytest.fixture(autouse=True)
    def get_page(self, base_url, selenium, testflask, refreshdb):  # noqa
        self.baseurl = base_url
        self.get(selenium, base_url + '/payperiods')

    def test_heading(self, selenium):
        heading = selenium.find_element_by_class_name('navbar-brand')
        assert heading.text == 'Pay Periods - BiweeklyBudget'

    def test_nav_menu(self, selenium):
        ul = selenium.find_element_by_id('side-menu')
        assert ul is not None
        assert 'nav' in ul.get_attribute('class')
        assert ul.tag_name == 'ul'

    def test_notifications(self, selenium):
        div = selenium.find_element_by_id('notifications-row')
        assert div is not None
        assert div.get_attribute('class') == 'row'


@pytest.mark.acceptance
class DONOTTestPayPeriodFor(AcceptanceHelper):

    def test_current_period(self, base_url, selenium):
        start_date = PAY_PERIOD_START_DATE
        print("PayPeriod start date: %s" % start_date)
        self.get(
            selenium,
            base_url + '/pay_period_for?date=' + start_date.strftime('%Y-%m-%d')
        )
        self.wait_for_load_complete(selenium)
        assert selenium.current_url == \
            base_url + '/payperiod/' + start_date.strftime('%Y-%m-%d')

    def test_current_period_end(self, base_url, selenium):
        start_date = PAY_PERIOD_START_DATE
        print("PayPeriod start date: %s" % start_date)
        send_date = start_date + timedelta(days=10)
        self.get(
            selenium,
            base_url + '/pay_period_for?date=' + send_date.strftime('%Y-%m-%d')
        )
        self.wait_for_load_complete(selenium)
        assert selenium.current_url == \
            base_url + '/payperiod/' + start_date.strftime('%Y-%m-%d')


@pytest.mark.acceptance
class TestFindPayPeriod(AcceptanceHelper):

    def test_input_date(self, base_url, selenium):
        self.get(selenium, base_url + '/payperiods')
        i = selenium.find_element_by_id('payperiod_date_input')
        i.clear()
        start_date = PAY_PERIOD_START_DATE
        print("PayPeriod start date: %s" % start_date)
        send_date = start_date + timedelta(days=4)
        i.send_keys(send_date.strftime('%Y-%m-%d'))
        selenium.find_element_by_id('payperiod-go-button').click()
        self.wait_for_load_complete(selenium)
        assert selenium.current_url == \
            base_url + '/payperiod/' + start_date.strftime('%Y-%m-%d')

    def test_input_calendar(self, base_url, selenium):
        self.get(selenium, base_url + '/payperiods')
        start_date = PAY_PERIOD_START_DATE
        print("PayPeriod start date: %s" % start_date)
        send_date = start_date + timedelta(days=4)
        if start_date.month > dtnow().month:
            daysdiv = selenium.find_element_by_xpath(
                '//div[@id="cal3"]//div[@class="datepicker-days"]'
            )
        else:
            daysdiv = selenium.find_element_by_xpath(
                '//div[@id="cal2"]//div[@class="datepicker-days"]'
            )
        tbl = daysdiv.find_elements_by_tag_name('table')[0]
        # month
        assert tbl.find_elements_by_tag_name(
            'thead')[0].find_elements_by_tag_name(
            'tr')[1].find_elements_by_tag_name('th')[1].text == \
            dtnow().strftime('%B %Y')
        tbody = tbl.find_elements_by_tag_name('tbody')[0]
        print('Looking for datepicker TD for date %s' % send_date)
        for e in tbody.find_elements_by_tag_name('td'):
            if (
                e.get_attribute('class') != 'day' and
                e.get_attribute('class') != 'today day'
            ):
                continue
            if e.text.strip() == str(send_date.day):
                parent = e.find_element_by_xpath('..')
                print("Found date TD: %s - parent: %s" % (
                    e.get_attribute('innerHTML'),
                    parent.get_attribute('innerHTML')
                ))
                e.click()
                break
        else:
            raise RuntimeError("Unable to find td for date %d", send_date.day)
        self.wait_for_load_complete(selenium)
        assert selenium.current_url == \
            base_url + '/payperiod/' + start_date.strftime('%Y-%m-%d')

    def test_input_calendar_future(self, base_url, selenium):
        self.get(selenium, base_url + '/payperiods')
        start_date = PAY_PERIOD_START_DATE
        print("PayPeriod start date: %s" % start_date)
        send_date = start_date + relativedelta(months=3)
        send_date = send_date.replace(day=3)
        send_pp = BiweeklyPayPeriod.period_for_date(send_date, None)
        daysdiv = selenium.find_element_by_xpath(
            '//div[@id="cal2"]//div[@class="datepicker-days"]'
        )
        tbl = daysdiv.find_elements_by_tag_name('table')[0]
        thead = tbl.find_elements_by_tag_name('thead')[0]
        # month
        assert thead.find_elements_by_tag_name(
            'tr')[1].find_elements_by_tag_name('th')[1].text == \
            dtnow().strftime('%B %Y')
        tbody = tbl.find_elements_by_tag_name('tbody')[0]
        print('Advancing by 3 months')
        next_link = thead.find_element_by_xpath('//th[@class="next"]')
        next_link.click()
        self.wait_for_jquery_done(selenium)
        next_link.click()
        self.wait_for_jquery_done(selenium)
        next_link.click()
        self.wait_for_jquery_done(selenium)
        print('Looking for datepicker TD for date %s' % send_date)
        for e in tbody.find_elements_by_tag_name('td'):
            if e.get_attribute('class') != 'day':
                continue
            if e.text.strip() == str(send_date.day):
                parent = e.find_element_by_xpath('..')
                print("Found date TD: %s - parent: %s" % (
                    e.get_attribute('innerHTML'),
                    parent.get_attribute('innerHTML')
                ))
                e.click()
                break
        else:
            raise RuntimeError("Unable to find td for date %d", send_date.day)
        self.wait_for_load_complete(selenium)
        assert selenium.current_url == \
            base_url + '/payperiod/' + send_pp.start_date.strftime('%Y-%m-%d')


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb')
class DONOTTestPayPeriodsIndex(AcceptanceHelper):

    def test_0_clean_db(self, testdb):
        # clean the database
        biweeklybudget.models.base.Base.metadata.reflect(engine)
        biweeklybudget.models.base.Base.metadata.drop_all(engine)
        biweeklybudget.models.base.Base.metadata.create_all(engine)

    def test_1_add_account(self, testdb):
        a = Account(
            description='First Bank Account',
            name='BankOne',
            ofx_cat_memo_to_name=True,
            ofxgetter_config_json='{"foo": "bar"}',
            vault_creds_path='secret/foo/bar/BankOne',
            acct_type=AcctType.Bank
        )
        testdb.add(a)
        a.set_balance(
            overall_date=datetime(2017, 4, 10, 12, 0, 0, tzinfo=UTC),
            ledger=1.0,
            ledger_date=datetime(2017, 4, 10, 12, 0, 0, tzinfo=UTC)
        )
        testdb.flush()
        testdb.commit()

    def test_2_add_budgets(self, testdb):
        testdb.add(Budget(
            name='1Income',
            is_periodic=True,
            description='1Income',
            starting_balance=1000.00,
            is_income=True
        ))
        testdb.add(Budget(
            name='2Periodic',
            is_periodic=True,
            description='2Periodic',
            starting_balance=500.00
        ))
        testdb.add(Budget(
            name='3Periodic',
            is_periodic=True,
            description='3Periodic',
            starting_balance=0.00
        ))
        testdb.flush()
        testdb.commit()

    def pay_periods(self, db):
        return {
            'prev': BiweeklyPayPeriod.period_for_date(
                (PAY_PERIOD_START_DATE - timedelta(days=2)), db),
            'curr': BiweeklyPayPeriod.period_for_date(
                PAY_PERIOD_START_DATE, db),
            'next': BiweeklyPayPeriod.period_for_date(
                (PAY_PERIOD_START_DATE + timedelta(days=15)), db),
            'following': BiweeklyPayPeriod.period_for_date(
                (PAY_PERIOD_START_DATE + timedelta(days=29)), db)
        }

    def test_3_add_transactions(self, testdb):
        acct = testdb.query(Account).get(1)
        ibudget = testdb.query(Budget).get(1)
        e1budget = testdb.query(Budget).get(2)
        e2budget = testdb.query(Budget).get(3)
        periods = self.pay_periods(testdb)
        # previous pay period
        ppdate = periods['prev'].start_date
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=1)),
            actual_amount=100.00,
            budgeted_amount=100.00,
            description='prev income',
            account=acct,
            budget=ibudget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=250.00,
            description='prev trans 1',
            account=acct,
            budget=e2budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=3)),
            actual_amount=600.00,
            budgeted_amount=500.00,
            description='prev trans 2',
            account=acct,
            budget=e1budget
        ))
        ppdate = periods['curr'].start_date
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=1)),
            actual_amount=1400.00,
            budgeted_amount=100.00,
            description='prev income',
            account=acct,
            budget=ibudget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=1850.00,
            description='prev trans 1',
            account=acct,
            budget=e2budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=3)),
            actual_amount=600.00,
            budgeted_amount=500.00,
            description='prev trans 2',
            account=acct,
            budget=e1budget
        ))
        ppdate = periods['next'].start_date
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=1)),
            actual_amount=1400.00,
            budgeted_amount=100.00,
            description='prev income',
            account=acct,
            budget=ibudget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=788.00,
            description='prev trans 1',
            account=acct,
            budget=e2budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=3)),
            actual_amount=600.00,
            budgeted_amount=500.00,
            description='prev trans 2',
            account=acct,
            budget=e1budget
        ))
        ppdate = periods['following'].start_date
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=1)),
            actual_amount=1400.00,
            budgeted_amount=100.00,
            description='prev income',
            account=acct,
            budget=ibudget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=2.00,
            description='prev trans 1',
            account=acct,
            budget=e2budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=3)),
            actual_amount=600.00,
            budgeted_amount=500.00,
            description='prev trans 2',
            account=acct,
            budget=e1budget
        ))
        testdb.flush()
        testdb.commit()

    def test_4_confirm_sums(self, testdb):
        periods = self.pay_periods(testdb)
        assert periods['prev'].overall_sums == {
            'allocated': 750.0,
            'spent': 850.0,
            'income': 1000.0,
            'remaining': 150.0
        }
        assert periods['curr'].overall_sums == {
            'allocated': 2350.0,
            'spent': 2450.0,
            'income': 1400.0,
            'remaining': -1050.0
        }
        assert periods['next'].overall_sums == {
            'allocated': 1288.0,
            'spent': 1388.0,
            'income': 1400.0,
            'remaining': 12.0
        }
        assert periods['following'].overall_sums == {
            'allocated': 502.0,
            'spent': 602.0,
            'income': 1400.0,
            'remaining': 798.0
        }

    def test_5_pay_periods_table(self, base_url, selenium, testdb):
        periods = self.pay_periods(testdb)
        self.get(selenium, base_url + '/payperiods')
        table = selenium.find_element_by_id('pay-period-table')
        texts = self.tbody2textlist(table)
        elems = self.tbody2elemlist(table)
        assert texts == [
            [
                periods['prev'].start_date.strftime('%Y-%m-%d'),
                '$750.00',
                '$850.00',
                '$150.00'
            ],
            [
                periods['curr'].start_date.strftime('%Y-%m-%d') + ' (current)',
                '$2,350.00',
                '$2,450.00',
                '-$1,050.00'
            ],
            [
                periods['next'].start_date.strftime('%Y-%m-%d'),
                '$1,288.00',
                '$1,388.00',
                '$12.00'
            ],
            [
                periods['following'].start_date.strftime('%Y-%m-%d'),
                '$502.00',
                '$602.00',
                '$798.00'
            ]
        ]
        # test links
        links = [x[0].get_attribute('innerHTML') for x in elems]
        expected = []
        for k in ['prev', 'curr', 'next', 'following']:
            dstr = periods[k].start_date.strftime('%Y-%m-%d')
            s = '<a href="/payperiod/%s">%s</a>' % (dstr, dstr)
            if k == 'curr':
                s += ' <em>(current)</em>'
            expected.append(s)
        assert links == expected
        # test red text for negative dollar amounts
        assert elems[0][3].get_attribute('innerHTML') == '$150.00'
        assert elems[1][3].get_attribute('innerHTML') == '<span ' \
            'class="text-danger">-$1,050.00</span>'
        # test highlighted row for current period
        tbody = table.find_element_by_tag_name('tbody')
        trs = tbody.find_elements_by_tag_name('tr')
        assert trs[1].get_attribute('class') == 'info'

    def test_6_notification_panels(self, base_url, selenium, testdb):
        periods = self.pay_periods(testdb)
        self.get(selenium, base_url + '/payperiods')
        this_panel = selenium.find_element_by_id('panel-period-current')
        assert this_panel.get_attribute('class') == 'panel panel-red'
        assert this_panel.find_element_by_class_name('panel-heading').text\
            == '-$1,050.00\nRemaining this period'
        assert this_panel.find_element_by_tag_name('a').get_attribute(
            'href') == base_url + '/payperiod/' + periods[
            'curr'].start_date.strftime('%Y-%m-%d')
        assert this_panel.find_element_by_class_name('panel-footer')\
            .text == 'View ' + periods['curr'].start_date.strftime(
            '%Y-%m-%d') + ' Pay Period'
        next_panel = selenium.find_element_by_id('panel-period-next')
        assert next_panel.get_attribute('class') == 'panel panel-yellow'
        assert next_panel.find_element_by_class_name('panel-heading').text \
            == '$12.00\nRemaining next period'
        assert next_panel.find_element_by_tag_name('a').get_attribute(
            'href') == base_url + '/payperiod/' + periods[
            'next'].start_date.strftime('%Y-%m-%d')
        assert next_panel.find_element_by_class_name('panel-footer')\
            .text == 'View ' + periods['next'].start_date.strftime(
            '%Y-%m-%d') + ' Pay Period'
        following_panel = selenium.find_element_by_id('panel-period-following')
        assert following_panel.get_attribute('class') == 'panel panel-green'
        assert following_panel.find_element_by_class_name('panel-heading')\
            .text == '$798.00\nRemaining following period'
        assert following_panel.find_element_by_tag_name('a').get_attribute(
            'href') == base_url + '/payperiod/' + periods[
            'following'].start_date.strftime('%Y-%m-%d')
        assert following_panel.find_element_by_class_name('panel-footer')\
            .text == 'View ' + periods['following'].start_date.strftime(
            '%Y-%m-%d') + ' Pay Period'


@pytest.mark.acceptance
class DONOTTestPayPeriod(AcceptanceHelper):

    @pytest.fixture(autouse=True)
    def get_page(self, base_url, selenium, testflask, refreshdb):  # noqa
        self.baseurl = base_url
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )

    def test_heading(self, selenium, testdb):
        heading = selenium.find_element_by_class_name('navbar-brand')
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        assert heading.text == '%s to %s Pay Period - BiweeklyBudget' % (
            pp.start_date.strftime('%Y-%m-%d'),
            pp.end_date.strftime('%Y-%m-%d')
        )

    def test_nav_menu(self, selenium):
        ul = selenium.find_element_by_id('side-menu')
        assert ul is not None
        assert 'nav' in ul.get_attribute('class')
        assert ul.tag_name == 'ul'

    def test_notifications(self, selenium):
        div = selenium.find_element_by_id('notifications-row')
        assert div is not None
        assert div.get_attribute('class') == 'row'


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb')
class DONOTTestPayPeriodOtherPeriodInfo(AcceptanceHelper):

    def test_0_clean_db(self, testdb):
        # clean the database
        biweeklybudget.models.base.Base.metadata.reflect(engine)
        biweeklybudget.models.base.Base.metadata.drop_all(engine)
        biweeklybudget.models.base.Base.metadata.create_all(engine)

    def test_1_add_account(self, testdb):
        a = Account(
            description='First Bank Account',
            name='BankOne',
            ofx_cat_memo_to_name=True,
            ofxgetter_config_json='{"foo": "bar"}',
            vault_creds_path='secret/foo/bar/BankOne',
            acct_type=AcctType.Bank
        )
        testdb.add(a)
        a.set_balance(
            overall_date=datetime(2017, 4, 10, 12, 0, 0, tzinfo=UTC),
            ledger=1.0,
            ledger_date=datetime(2017, 4, 10, 12, 0, 0, tzinfo=UTC)
        )
        testdb.flush()
        testdb.commit()

    def test_2_add_budgets(self, testdb):
        testdb.add(Budget(
            name='1Income',
            is_periodic=True,
            description='1Income',
            starting_balance=1000.00,
            is_income=True
        ))
        testdb.add(Budget(
            name='2Periodic',
            is_periodic=True,
            description='2Periodic',
            starting_balance=500.00
        ))
        testdb.add(Budget(
            name='3Periodic',
            is_periodic=True,
            description='3Periodic',
            starting_balance=0.00
        ))
        testdb.flush()
        testdb.commit()

    def pay_periods(self, db):
        return {
            'prev': BiweeklyPayPeriod.period_for_date(
                (PAY_PERIOD_START_DATE - timedelta(days=2)), db),
            'curr': BiweeklyPayPeriod.period_for_date(
                PAY_PERIOD_START_DATE, db),
            'next': BiweeklyPayPeriod.period_for_date(
                (PAY_PERIOD_START_DATE + timedelta(days=15)), db),
            'following': BiweeklyPayPeriod.period_for_date(
                (PAY_PERIOD_START_DATE + timedelta(days=29)), db),
            'last': BiweeklyPayPeriod.period_for_date(
                (PAY_PERIOD_START_DATE + timedelta(days=43)), db)
        }

    def test_3_add_transactions(self, testdb):
        acct = testdb.query(Account).get(1)
        ibudget = testdb.query(Budget).get(1)
        e1budget = testdb.query(Budget).get(2)
        e2budget = testdb.query(Budget).get(3)
        periods = self.pay_periods(testdb)
        # previous pay period
        ppdate = periods['prev'].start_date
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=1)),
            actual_amount=100.00,
            budgeted_amount=100.00,
            description='prev income',
            account=acct,
            budget=ibudget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=250.00,
            description='prev trans 1',
            account=acct,
            budget=e2budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=3)),
            actual_amount=600.00,
            budgeted_amount=500.00,
            description='prev trans 2',
            account=acct,
            budget=e1budget
        ))
        ppdate = periods['curr'].start_date
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=1)),
            actual_amount=1400.00,
            budgeted_amount=100.00,
            description='curr income',
            account=acct,
            budget=ibudget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=1850.00,
            description='curr trans 1',
            account=acct,
            budget=e2budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=3)),
            actual_amount=600.00,
            budgeted_amount=500.00,
            description='curr trans 2',
            account=acct,
            budget=e1budget
        ))
        ppdate = periods['next'].start_date
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=1)),
            actual_amount=1400.00,
            budgeted_amount=100.00,
            description='next income',
            account=acct,
            budget=ibudget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=788.00,
            description='next trans 1',
            account=acct,
            budget=e2budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=3)),
            actual_amount=600.00,
            budgeted_amount=500.00,
            description='next trans 2',
            account=acct,
            budget=e1budget
        ))
        ppdate = periods['following'].start_date
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=1)),
            actual_amount=1400.00,
            budgeted_amount=100.00,
            description='following income',
            account=acct,
            budget=ibudget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=2.00,
            description='following trans 1',
            account=acct,
            budget=e2budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=3)),
            actual_amount=600.00,
            budgeted_amount=500.00,
            description='following trans 2',
            account=acct,
            budget=e1budget
        ))
        ppdate = periods['last'].start_date
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=1)),
            actual_amount=1400.00,
            budgeted_amount=100.00,
            description='last income',
            account=acct,
            budget=ibudget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=2.00,
            description='last trans 1',
            account=acct,
            budget=e2budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=3)),
            actual_amount=550.00,
            budgeted_amount=550.00,
            description='last trans 2',
            account=acct,
            budget=e1budget
        ))
        testdb.flush()
        testdb.commit()

    def test_4_confirm_sums(self, testdb):
        periods = self.pay_periods(testdb)
        assert periods['prev'].overall_sums == {
            'allocated': 750.0,
            'spent': 850.0,
            'income': 1000.0,
            'remaining': 150.0
        }
        assert periods['curr'].overall_sums == {
            'allocated': 2350.0,
            'spent': 2450.0,
            'income': 1400.0,
            'remaining': -1050.0
        }
        assert periods['next'].overall_sums == {
            'allocated': 1288.0,
            'spent': 1388.0,
            'income': 1400.0,
            'remaining': 12.0
        }
        assert periods['following'].overall_sums == {
            'allocated': 502.0,
            'spent': 602.0,
            'income': 1400.0,
            'remaining': 798.0
        }
        assert periods['last'].overall_sums == {
            'allocated': 552.0,
            'spent': 552.0,
            'income': 1400.0,
            'remaining': 848.0
        }

    def test_5_other_periods_table(self, base_url, selenium, testdb):
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        table = selenium.find_element_by_id('pay-period-table')
        assert self.thead2list(table) == [
            '%s (prev.)' % pp.previous.start_date.strftime('%Y-%m-%d'),
            '%s (curr.)' % pp.start_date.strftime('%Y-%m-%d'),
            '%s (next)' % pp.next.start_date.strftime('%Y-%m-%d'),
            '%s' % pp.next.next.start_date.strftime('%Y-%m-%d'),
            '%s' % pp.next.next.next.start_date.strftime('%Y-%m-%d')
        ]
        assert self.tbody2textlist(table) == [[
            '$150.00',
            '-$1,050.00',
            '$12.00',
            '$798.00',
            '$848.00'
        ]]
        contents = [
            x.get_attribute('innerHTML') for x in self.thead2elemlist(table)
        ]
        assert contents == [
            '<a href="/payperiod/{d}">{d} <em>(prev.)</em></a>'.format(
                d=pp.previous.start_date.strftime('%Y-%m-%d')),
            '{d} <em>(curr.)</em>'.format(
                d=pp.start_date.strftime('%Y-%m-%d')),
            '<a href="/payperiod/{d}">{d} <em>(next)</em></a>'.format(
                d=pp.next.start_date.strftime('%Y-%m-%d')),
            '<a href="/payperiod/{d}">{d}</a>'.format(
                d=pp.next.next.start_date.strftime('%Y-%m-%d')),
            '<a href="/payperiod/{d}">{d}</a>'.format(
                d=pp.next.next.next.start_date.strftime('%Y-%m-%d'))
        ]


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb')
class DONOTTestCurrentPayPeriod(AcceptanceHelper):

    def test_00_inactivate_scheduled(self, testdb):
        for s in testdb.query(
                ScheduledTransaction).filter(
            ScheduledTransaction.is_active.__eq__(True)
        ).all():
            s.is_active = False
            testdb.add(s)
        testdb.flush()
        testdb.commit()
        # delete existing transactions
        for tr in testdb.query(TxnReconcile).all():
            testdb.delete(tr)
        for idx in [1, 2, 3]:
            t = testdb.query(Transaction).get(idx)
            testdb.delete(t)
        testdb.flush()
        testdb.commit()

    def test_01_add_transactions(self, testdb):
        acct = testdb.query(Account).get(1)
        e1budget = testdb.query(Budget).get(1)
        e2budget = testdb.query(Budget).get(2)
        pp = BiweeklyPayPeriod.period_for_date(
            PAY_PERIOD_START_DATE, testdb
        )
        ppdate = pp.start_date
        st = ScheduledTransaction(
            account=acct,
            budget=e1budget,
            amount=11.11,
            num_per_period=2,
            description='ST7 per_period'
        )
        testdb.add(st)
        testdb.add(ScheduledTransaction(
            account=acct,
            budget=e1budget,
            amount=22.22,
            day_of_month=(ppdate + timedelta(days=5)).day,
            description='ST8 day_of_month'
        ))
        testdb.add(ScheduledTransaction(
            account=acct,
            budget=e2budget,
            amount=33.33,
            date=(ppdate + timedelta(days=6)),
            description='ST9 date'
        ))
        t = Transaction(
            date=(ppdate + timedelta(days=8)),
            actual_amount=12.00,
            budgeted_amount=11.11,
            description='Txn From ST7',
            account=acct,
            budget=e1budget,
            scheduled_trans=st
        )
        testdb.add(t)
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=6)),
            actual_amount=111.13,
            budgeted_amount=111.11,
            description='T1foo',
            notes='notesT1',
            account=acct,
            scheduled_trans=testdb.query(ScheduledTransaction).get(1),
            budget=e1budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=-333.33,
            budgeted_amount=-333.33,
            description='T2',
            notes='notesT2',
            account=testdb.query(Account).get(2),
            scheduled_trans=testdb.query(ScheduledTransaction).get(3),
            budget=testdb.query(Budget).get(4)
        ))
        testdb.add(Transaction(
            date=ppdate,
            actual_amount=222.22,
            description='T3',
            notes='notesT3',
            account=testdb.query(Account).get(3),
            budget=e2budget
        ))
        testdb.flush()
        testdb.commit()
        testdb.add(TxnReconcile(note='foo', txn_id=t.id))
        testdb.flush()
        testdb.commit()

    def test_03_info_panels(self, base_url, selenium, testdb):
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        assert selenium.find_element_by_id(
            'amt-income').text == '$2,345.67'
        assert selenium.find_element_by_id('amt-allocated').text == '$411.10'
        assert selenium.find_element_by_id('amt-spent').text == '$345.35'
        assert selenium.find_element_by_id('amt-remaining').text == '$1,934.57'

    def test_04_periodic_budgets(self, base_url, selenium, testdb):
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        table = selenium.find_element_by_id('pb-table')
        elems = self.tbody2elemlist(table)
        htmls = []
        for row in elems:
            htmls.append(
                [x.get_attribute('innerHTML') for x in row]
            )
        assert htmls == [
            [
                '<a href="/budgets/1">Periodic1</a>',
                '$100.00',
                '$155.55',
                '$123.13',
                '<span class="text-danger">-$56.46</span>'
            ],
            [
                '<a href="/budgets/2">Periodic2</a>',
                '$234.00',
                '$255.55',
                '$222.22',
                '<span class="text-danger">-$21.55</span>'
            ],
            [
                '<a href="/budgets/7">Income (i)</a>',
                '$2,345.67',
                '$0.00',
                '$0.00',
                '$2,345.67'
            ]
        ]

    def test_05_standing_budgets(self, base_url, selenium, testdb):
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        table = selenium.find_element_by_id('sb-table')
        elems = self.tbody2elemlist(table)
        htmls = []
        for row in elems:
            htmls.append(
                [x.get_attribute('innerHTML') for x in row]
            )
        assert htmls == [
            [
                '<a href="/budgets/4">Standing1</a>',
                '$1,284.23'
            ],
            [
                '<a href="/budgets/5">Standing2</a>',
                '$9,482.29'
            ]
        ]

    def test_06_add_trans_button(self, base_url, selenium, testdb):
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        btn = selenium.find_element_by_id('btn-add-txn')
        btn.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Add New Transaction'

    def test_07_transaction_table(self, base_url, selenium, testdb):
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        ppdate = pp.start_date
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        table = selenium.find_element_by_id('trans-table')
        elems = self.tbody2elemlist(table)
        htmls = []
        for row in elems:
            htmls.append(
                [x.get_attribute('innerHTML') for x in row]
            )
        assert htmls == [
            [
                '',
                '$11.11',
                '<em>(sched)</em> <a href="javascript:schedModal(7, null);">'
                'ST7 per_period (7)</a>',
                '<a href="/accounts/1">BankOne</a>',
                '<a href="/budgets/1">Periodic1</a>',
                '<a href="javascript:schedToTransModal(7, \'%s\');">make '
                'trans.</a>' % pp.start_date.strftime('%Y-%m-%d'),
                '&nbsp;'
            ],
            [
                ppdate.strftime('%Y-%m-%d'),
                '$222.22',
                '<a href="javascript:transModal(7, null);">T3 (7)</a>',
                '<a href="/accounts/3">CreditOne</a>',
                '<a href="/budgets/2">Periodic2</a>',
                '&nbsp;',
                '&nbsp;'
            ],
            [
                (ppdate + timedelta(days=2)).strftime('%Y-%m-%d'),
                '-$333.33',
                '<a href="javascript:transModal(6, null);">T2 (6)</a>',
                '<a href="/accounts/2">BankTwoStale</a>',
                '<a href="/budgets/4">Standing1</a>',
                '<em>(from <a href="javascript:schedModal(3, null);">3</a>)'
                '</em>',
                '&nbsp;'
            ],
            [
                (pp.start_date + timedelta(days=5)).strftime('%Y-%m-%d'),
                '$22.22',
                '<em>(sched)</em> <a href="javascript:schedModal(8, null);">'
                'ST8 day_of_month (8)</a>',
                '<a href="/accounts/1">BankOne</a>',
                '<a href="/budgets/1">Periodic1</a>',
                '<a href="javascript:schedToTransModal(8, \'%s\');">make '
                'trans.</a>' % pp.start_date.strftime('%Y-%m-%d'),
                '&nbsp;'
            ],
            [
                (ppdate + timedelta(days=6)).strftime('%Y-%m-%d'),
                '$111.13',
                '<a href="javascript:transModal(5, null);">T1foo (5)</a>',
                '<a href="/accounts/1">BankOne</a>',
                '<a href="/budgets/1">Periodic1</a>',
                '<em>(from <a href="javascript:schedModal(1, null);">1</a>)'
                '</em>',
                '&nbsp;'
            ],
            [
                (pp.start_date + timedelta(days=6)).strftime('%Y-%m-%d'),
                '$33.33',
                '<em>(sched)</em> <a href="javascript:schedModal(9, null);">'
                'ST9 date (9)</a>',
                '<a href="/accounts/1">BankOne</a>',
                '<a href="/budgets/2">Periodic2</a>',
                '<a href="javascript:schedToTransModal(9, \'%s\');">make '
                'trans.</a>' % pp.start_date.strftime('%Y-%m-%d'),
                '&nbsp;'
            ],
            [
                (pp.start_date + timedelta(days=8)).strftime('%Y-%m-%d'),
                '$12.00',
                '<a href="javascript:transModal(4, null);">Txn From ST7'
                ' (4)</a>',
                '<a href="/accounts/1">BankOne</a>',
                '<a href="/budgets/1">Periodic1</a>',
                '<em>(from <a href="javascript:schedModal(7, null);">7</a>)'
                '</em>',
                '<a href="javascript:txnReconcileModal(2)">Yes (2)</a>'
            ]
        ]

    def test_08_transaction_modal(self, base_url, selenium, testdb):
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        link = selenium.find_element_by_xpath('//a[text()="T1foo (5)"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Transaction 5'
        assert body.find_element_by_id(
            'trans_frm_id').get_attribute('value') == '5'
        assert body.find_element_by_id(
            'trans_frm_date').get_attribute('value') == (
            pp.start_date + timedelta(days=6)).strftime('%Y-%m-%d')
        assert body.find_element_by_id(
            'trans_frm_amount').get_attribute('value') == '111.13'
        assert body.find_element_by_id(
            'trans_frm_description').get_attribute('value') == 'T1foo'
        acct_sel = Select(body.find_element_by_id('trans_frm_account'))
        opts = []
        for o in acct_sel.options:
            opts.append([o.get_attribute('value'), o.text])
        assert opts == [
            ['None', ''],
            ['1', 'BankOne'],
            ['2', 'BankTwoStale'],
            ['3', 'CreditOne'],
            ['4', 'CreditTwo'],
            ['6', 'DisabledBank'],
            ['5', 'InvestmentOne']
        ]
        assert acct_sel.first_selected_option.get_attribute('value') == '1'
        budget_sel = Select(body.find_element_by_id('trans_frm_budget'))
        opts = []
        for o in budget_sel.options:
            opts.append([o.get_attribute('value'), o.text])
        assert opts == [
            ['None', ''],
            ['1', 'Periodic1'],
            ['2', 'Periodic2'],
            ['3', 'Periodic3 Inactive'],
            ['4', 'Standing1'],
            ['5', 'Standing2'],
            ['6', 'Standing3 Inactive'],
            ['7', 'Income (i)']
        ]
        assert budget_sel.first_selected_option.get_attribute('value') == '1'
        assert selenium.find_element_by_id(
            'trans_frm_notes').get_attribute('value') == 'notesT1'

    def test_09_transaction_modal_edit(self, base_url, selenium, testdb):
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        link = selenium.find_element_by_xpath('//a[text()="T1foo (5)"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Transaction 5'
        assert body.find_element_by_id(
            'trans_frm_id').get_attribute('value') == '5'
        desc = body.find_element_by_id('trans_frm_description')
        desc.send_keys('edited')
        # submit the form
        selenium.find_element_by_id('modalSaveButton').click()
        self.wait_for_jquery_done(selenium)
        # check that we got positive confirmation
        _, _, body = self.get_modal_parts(selenium)
        x = body.find_elements_by_tag_name('div')[0]
        assert 'alert-success' in x.get_attribute('class')
        assert x.text.strip() == 'Successfully saved Transaction 5 ' \
                                 'in database.'
        # dismiss the modal
        selenium.find_element_by_id('modalCloseButton').click()
        self.wait_for_load_complete(selenium)
        # test that updated budget was removed from the page
        table = selenium.find_element_by_id('trans-table')
        texts = [y[2] for y in self.tbody2textlist(table)]
        assert 'T1fooedited (5)' in texts

    def test_10_transaction_modal_verify_db(self, testdb):
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        t = testdb.query(Transaction).get(5)
        assert t is not None
        assert t.description == 'T1fooedited'
        assert t.date == (pp.start_date + timedelta(days=6))
        assert float(t.actual_amount) == 111.13
        assert float(t.budgeted_amount) == 111.11
        assert t.account_id == 1
        assert t.budget_id == 1
        assert t.scheduled_trans_id == 1
        assert t.notes == 'notesT1'

    def test_11_sched_trans_verify_db(self, testdb):
        t = testdb.query(ScheduledTransaction).get(7)
        assert t is not None
        assert t.description == 'ST7 per_period'
        assert t.num_per_period == 2
        assert t.date is None
        assert t.day_of_month is None
        assert float(t.amount) == 11.11
        assert t.account_id == 1
        assert t.budget_id == 1
        assert t.notes is None
        assert t.is_active is True

    def test_12_sched_trans_modal(self, base_url, selenium):
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        link = selenium.find_element_by_xpath(
            '//a[text()="ST7 per_period (7)"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Edit Scheduled Transaction 7'
        assert body.find_element_by_id(
            'sched_frm_id').get_attribute('value') == '7'
        assert body.find_element_by_id(
            'sched_frm_description').get_attribute('value') == 'ST7 per_period'
        assert body.find_element_by_id(
            'sched_frm_type_monthly').is_selected() is False
        assert body.find_element_by_id(
            'sched_frm_type_date').is_selected() is False
        assert body.find_element_by_id(
            'sched_frm_type_per_period').is_selected()
        assert body.find_element_by_id(
            'sched_frm_num_per_period').get_attribute('value') == '2'
        assert body.find_element_by_id(
            'sched_frm_amount').get_attribute('value') == '11.11'
        acct_sel = Select(body.find_element_by_id('sched_frm_account'))
        assert acct_sel.first_selected_option.get_attribute('value') == '1'
        budget_sel = Select(body.find_element_by_id('sched_frm_budget'))
        assert budget_sel.first_selected_option.get_attribute('value') == '1'
        assert selenium.find_element_by_id(
            'sched_frm_active').is_selected()

    def test_13_sched_trans_modal_edit(self, base_url, selenium):
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        link = selenium.find_element_by_xpath(
            '//a[text()="ST7 per_period (7)"]')
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        desc = body.find_element_by_id('sched_frm_description')
        desc.send_keys('edited')
        # submit the form
        selenium.find_element_by_id('modalSaveButton').click()
        self.wait_for_jquery_done(selenium)
        # check that we got positive confirmation
        _, _, body = self.get_modal_parts(selenium)
        x = body.find_elements_by_tag_name('div')[0]
        assert 'alert-success' in x.get_attribute('class')
        assert x.text.strip() == 'Successfully saved ScheduledTransaction 7 ' \
                                 'in database.'
        # dismiss the modal
        selenium.find_element_by_id('modalCloseButton').click()
        self.wait_for_load_complete(selenium)
        # test that updated budget was removed from the page
        table = selenium.find_element_by_id('trans-table')
        texts = self.tbody2textlist(table)
        # sort order changes when we make this active
        assert texts[0][2] == '(sched) ST7 per_periodedited (7)'

    def test_14_sched_trans_modal_verify_db(self, testdb):
        t = testdb.query(ScheduledTransaction).get(7)
        assert t is not None
        assert t.description == 'ST7 per_periodedited'
        assert t.num_per_period == 2
        assert t.date is None
        assert t.day_of_month is None
        assert float(t.amount) == 11.11
        assert t.account_id == 1
        assert t.budget_id == 1
        assert t.notes == ''
        assert t.is_active is True


@pytest.mark.acceptance
@pytest.mark.usefixtures('class_refresh_db', 'refreshdb')
class DONOTTestMakeTransModal(AcceptanceHelper):

    def test_00_inactivate_scheduled(self, testdb):
        for s in testdb.query(
                ScheduledTransaction).filter(
            ScheduledTransaction.is_active.__eq__(True)
        ).all():
            s.is_active = False
            testdb.add(s)
        testdb.flush()
        testdb.commit()
        # delete existing transactions
        for tr in testdb.query(TxnReconcile).all():
            testdb.delete(tr)
        for idx in [1, 2, 3]:
            t = testdb.query(Transaction).get(idx)
            testdb.delete(t)
        testdb.flush()
        testdb.commit()

    def test_01_add_sched_transaction(self, testdb):
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        ppdate = pp.start_date
        acct = testdb.query(Account).get(1)
        e1budget = testdb.query(Budget).get(1)
        testdb.add(ScheduledTransaction(
            account=acct,
            budget=e1budget,
            amount=11.11,
            num_per_period=2,
            description='ST7 per_period'
        ))
        testdb.flush()
        testdb.commit()
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=6)),
            actual_amount=111.13,
            budgeted_amount=111.11,
            description='T1foo',
            notes='notesT1',
            account=acct,
            scheduled_trans=testdb.query(ScheduledTransaction).get(1),
            budget=e1budget
        ))
        testdb.add(Transaction(
            date=(ppdate + timedelta(days=2)),
            actual_amount=-333.33,
            budgeted_amount=-333.33,
            description='T2',
            notes='notesT2',
            account=testdb.query(Account).get(2),
            scheduled_trans=testdb.query(ScheduledTransaction).get(3),
            budget=testdb.query(Budget).get(4)
        ))
        testdb.add(Transaction(
            date=ppdate,
            actual_amount=222.22,
            description='T3',
            notes='notesT3',
            account=testdb.query(Account).get(3),
            budget=testdb.query(Budget).get(2)
        ))

    def test_02_transaction_table(self, base_url, selenium, testdb):
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        table = selenium.find_element_by_id('trans-table')
        elems = self.tbody2elemlist(table)
        htmls = []
        for row in elems:
            htmls.append(
                [x.get_attribute('innerHTML') for x in row]
            )
        assert htmls == [
            [
                '',
                '$11.11',
                '<em>(sched)</em> <a href="javascript:schedModal(7, null);">'
                'ST7 per_period (7)</a>',
                '<a href="/accounts/1">BankOne</a>',
                '<a href="/budgets/1">Periodic1</a>',
                '<a href="javascript:schedToTransModal(7, \'%s\');">make '
                'trans.</a>' % pp.start_date.strftime('%Y-%m-%d'),
                '&nbsp;'
            ],
            [
                '',
                '$11.11',
                '<em>(sched)</em> <a href="javascript:schedModal(7, null);">'
                'ST7 per_period (7)</a>',
                '<a href="/accounts/1">BankOne</a>',
                '<a href="/budgets/1">Periodic1</a>',
                '<a href="javascript:schedToTransModal(7, \'%s\');">make '
                'trans.</a>' % pp.start_date.strftime('%Y-%m-%d'),
                '&nbsp;'
            ]
        ]

    def test_03_verify_db(self, testdb):
        t = testdb.query(ScheduledTransaction).get(7)
        assert t is not None
        assert t.description == 'ST7 per_period'
        assert t.num_per_period == 2
        assert t.date is None
        assert t.day_of_month is None
        assert float(t.amount) == 11.11
        assert t.account_id == 1
        assert t.budget_id == 1
        assert t.notes is None
        assert t.is_active is True

    def test_04_make_trans_modal_num_per(self, base_url, selenium, testdb):
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        link = selenium.find_elements_by_xpath(
            '//a[@href="javascript:schedToTransModal(7, \'%s\');"]'
            '' % pp.start_date.strftime('%Y-%m-%d'))[0]
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        assert title.text == 'Scheduled Transaction 7 to Transaction'
        assert body.find_element_by_id(
            'schedtotrans_frm_id').get_attribute('value') == '7'
        assert body.find_element_by_id(
            'schedtotrans_frm_pp_date').get_attribute(
            'value') == pp.start_date.strftime('%Y-%m-%d')
        # if a num_per_period scheduled transaction, default to today
        # this default is populated by JS, which will use localtime
        assert body.find_element_by_id(
            'schedtotrans_frm_date').get_attribute(
            'value') == datetime.now().strftime('%Y-%m-%d')
        assert body.find_element_by_id(
            'schedtotrans_frm_amount').get_attribute('value') == '11.11'
        assert body.find_element_by_id(
            'schedtotrans_frm_description').get_attribute(
            'value') == 'ST7 per_period'
        assert body.find_element_by_id(
            'schedtotrans_frm_notes').get_attribute(
            'value') == ''

    def test_05_edit_modal(self, base_url, selenium, testdb):
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        self.get(
            selenium,
            base_url + '/payperiod/' +
            PAY_PERIOD_START_DATE.strftime('%Y-%m-%d')
        )
        link = selenium.find_elements_by_xpath(
            '//a[@href="javascript:schedToTransModal(7, \'%s\');"]'
            '' % pp.start_date.strftime('%Y-%m-%d'))[0]
        link.click()
        modal, title, body = self.get_modal_parts(selenium)
        self.assert_modal_displayed(modal, title, body)
        body.find_element_by_id('schedtotrans_frm_date').clear()
        body.find_element_by_id('schedtotrans_frm_date').send_keys(
            (pp.start_date + timedelta(days=2)).strftime('%Y-%m-%d')
        )
        body.find_element_by_id('schedtotrans_frm_amount').clear()
        body.find_element_by_id('schedtotrans_frm_amount').send_keys('22.22')
        body.find_element_by_id('schedtotrans_frm_description').send_keys(
            ' Trans'
        )
        body.find_element_by_id('schedtotrans_frm_notes').clear()
        body.find_element_by_id('schedtotrans_frm_notes').send_keys('T4notes')
        # submit the form
        selenium.find_element_by_id('modalSaveButton').click()
        self.wait_for_jquery_done(selenium)
        # check that we got positive confirmation
        _, _, body = self.get_modal_parts(selenium)
        x = body.find_elements_by_tag_name('div')[0]
        assert 'alert-success' in x.get_attribute('class')
        assert x.text.strip() == 'Successfully created Transaction 6 for ' \
                                 'ScheduledTransaction 7.'
        # dismiss the modal
        selenium.find_element_by_id('modalCloseButton').click()
        self.wait_for_load_complete(selenium)
        # test that updated budget was removed from the page
        table = selenium.find_element_by_id('trans-table')
        texts = self.tbody2textlist(table)
        # sort order changes when we make this active
        assert texts[0][2] == '(sched) ST7 per_period (7)'
        assert texts[1][2] == 'ST7 per_period Trans (6)'

    def test_06_verify_db(self, testdb):
        t = testdb.query(ScheduledTransaction).get(7)
        assert t is not None
        assert t.description == 'ST7 per_period'
        assert t.num_per_period == 2
        assert t.date is None
        assert t.day_of_month is None
        assert float(t.amount) == 11.11
        assert t.account_id == 1
        assert t.budget_id == 1
        assert t.notes is None
        assert t.is_active is True
        pp = BiweeklyPayPeriod(PAY_PERIOD_START_DATE, testdb)
        t = testdb.query(Transaction).get(6)
        assert t is not None
        assert t.description == 'ST7 per_period Trans'
        assert t.date == (pp.start_date + timedelta(days=2))
        assert float(t.actual_amount) == 22.22
        assert float(t.budgeted_amount) == 11.11
        assert t.account_id == 1
        assert t.budget_id == 1
        assert t.scheduled_trans_id == 7
        assert t.notes == 'T4notes'
