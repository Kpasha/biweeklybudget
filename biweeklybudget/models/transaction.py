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
either as a pull request on GitHub, or to me via email.
################################################################################

AUTHORS:
Jason Antman <jason@jasonantman.com> <http://www.jasonantman.com>
################################################################################
"""

from sqlalchemy import Column, Integer, Numeric, String, Date, ForeignKey
from sqlalchemy.orm import relationship
from biweeklybudget.models.base import Base, ModelAsDict
from biweeklybudget.utils import dtnow


class Transaction(Base, ModelAsDict):

    __tablename__ = 'transactions'
    __table_args__ = (
        {'mysql_engine': 'InnoDB'}
    )

    # Primary Key
    id = Column(Integer, primary_key=True)

    date = Column(Date, default=dtnow())

    actual_amount = Column(Numeric(precision=10, scale=4), nullable=False)

    budgeted_amount = Column(Numeric(precision=10, scale=4))

    description = Column(String(254), nullable=False, index=True)

    notes = Column(String(254))

    account_id = Column(Integer, ForeignKey('accounts.id'))
    account = relationship(
        "Account", backref="transactions", uselist=False
    )

    # set when a scheduled transaction is converted to a real one
    scheduled_trans_id = Column(
        Integer, ForeignKey('scheduled_transactions.id')
    )
    scheduled_trans = relationship(
        "ScheduledTransaction", backref="transactions", uselist=False
    )

    budget_id = Column(Integer, ForeignKey('budgets.id'))
    budget = relationship(
        "Budget", backref="transactions", uselist=False
    )

    def __repr__(self):
        return "<Transaction(id=%d)>" % (
            self.id
        )