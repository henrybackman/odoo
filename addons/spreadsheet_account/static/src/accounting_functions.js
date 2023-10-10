/** @odoo-module **/

import { _lt, _t } from "@web/core/l10n/translation";
import { sprintf } from "@web/core/utils/strings";

import spreadsheet from "@spreadsheet/o_spreadsheet/o_spreadsheet_extended";
const { functionRegistry } = spreadsheet.registries;
const { arg, toBoolean, toString, toNumber, toJsDate } = spreadsheet.helpers;

const QuarterRegexp = /^q([1-4])\/(\d{4})$/i;
const MonthRegexp = /^0?([1-9]|1[0-2])\/(\d{4})$/i;

/**
 * @typedef {Object} YearDateRange
 * @property {"year"} rangeType
 * @property {number} year
 */

/**
 * @typedef {Object} QuarterDateRange
 * @property {"quarter"} rangeType
 * @property {number} year
 * @property {number} quarter
 */

/**
 * @typedef {Object} MonthDateRange
 * @property {"month"} rangeType
 * @property {number} year
 * @property {number} month
 */

/**
 * @typedef {Object} DayDateRange
 * @property {"day"} rangeType
 * @property {number} year
 * @property {number} month
 * @property {number} day
 */

/**
 * @typedef {YearDateRange | QuarterDateRange | MonthDateRange | DayDateRange} DateRange
 */

/**
 * @param {string} dateRange
 * @returns {QuarterDateRange | undefined}
 */
function parseAccountingQuarter(dateRange) {
    const found = dateRange.match(QuarterRegexp);
    return found
        ? {
              rangeType: "quarter",
              year: toNumber(found[2]),
              quarter: toNumber(found[1]),
          }
        : undefined;
}

/**
 * @param {string} dateRange
 * @returns {MonthDateRange | undefined}
 */
function parseAccountingMonth(dateRange) {
    const found = dateRange.match(MonthRegexp);
    return found
        ? {
              rangeType: "month",
              year: toNumber(found[2]),
              month: toNumber(found[1]),
          }
        : undefined;
}

/**
 * @param {string} dateRange
 * @returns {YearDateRange | undefined}
 */
function parseAccountingYear(dateRange) {
    const dateNumber = toNumber(dateRange);
    // This allows a bit of flexibility for the user if they were to input a
    // numeric value instead of a year.
    // Users won't need to fetch accounting info for year 3000 before a long time
    // And the numeric value 3000 corresponds to 18th march 1908, so it's not an
    //issue to prevent them from fetching accounting data prior to that date.
    if (dateNumber < 3000) {
        return { rangeType: "year", year: dateNumber };
    }
    return undefined;
}

/**
 * @param {string} dateRange
 * @returns {DayDateRange}
 */
function parseAccountingDay(dateRange) {
    const dateNumber = toNumber(dateRange);
    return {
        rangeType: "day",
        year: functionRegistry.get("YEAR").compute(dateNumber),
        month: functionRegistry.get("MONTH").compute(dateNumber),
        day: functionRegistry.get("DAY").compute(dateNumber),
    };
}

/**
 * @param {string | number} dateRange
 * @returns {DateRange}
 */
export function parseAccountingDate(dateRange) {
    try {
        dateRange = toString(dateRange).trim();
        return (
            parseAccountingQuarter(dateRange) ||
            parseAccountingMonth(dateRange) ||
            parseAccountingYear(dateRange) ||
            parseAccountingDay(dateRange)
        );
    } catch {
        throw new Error(
            sprintf(
                _t(
                    `'%s' is not a valid period. Supported formats are "21/12/2022", "Q1/2022", "12/2022", and "2022".`
                ),
                dateRange
            )
        );
    }
}

const ODOO_FIN_ARGS = () => [
    arg("account_codes (string)", _lt("The prefix of the accounts.")),
    arg(
        "date_range (string, date)",
        _lt(`The date range. Supported formats are "21/12/2022", "Q1/2022", "12/2022", and "2022".`)
    ),
    arg("offset (number, default=0)", _lt("Year offset applied to date_range.")),
    arg("company_id (number, optional)", _lt("The company to target (Advanced).")),
    arg("include_unposted (boolean, default=FALSE)", _lt("Set to TRUE to include unposted entries.")),
];

functionRegistry.add("ODOO.CREDIT", {
    description: _lt("Get the total credit for the specified account(s) and period."),
    args: ODOO_FIN_ARGS(),
    returns: ["NUMBER"],
    compute: function (
        accountCodes,
        dateRange,
        offset = 0,
        companyId = null,
        includeUnposted = false
    ) {
        accountCodes = toString(accountCodes)
            .split(",")
            .map((code) => code.trim())
            .sort();
        offset = toNumber(offset);
        dateRange = parseAccountingDate(dateRange);
        includeUnposted = toBoolean(includeUnposted);
        return this.getters.getAccountPrefixCredit(
            accountCodes,
            dateRange,
            offset,
            companyId,
            includeUnposted
        );
    },
    computeFormat: function (
        accountCodes,
        dateRange,
        offset = 0,
        companyId = null,
        includeUnposted = false
    ) {
        return this.getters.getCompanyCurrencyFormat(companyId && companyId.value) || "#,##0.00";
    },
});

functionRegistry.add("ODOO.DEBIT", {
    description: _lt("Get the total debit for the specified account(s) and period."),
    args: ODOO_FIN_ARGS(),
    returns: ["NUMBER"],
    compute: function (
        accountCodes,
        dateRange,
        offset = 0,
        companyId = null,
        includeUnposted = false
    ) {
        accountCodes = toString(accountCodes)
            .split(",")
            .map((code) => code.trim())
            .sort();
        offset = toNumber(offset);
        dateRange = parseAccountingDate(dateRange);
        includeUnposted = toBoolean(includeUnposted);
        return this.getters.getAccountPrefixDebit(
            accountCodes,
            dateRange,
            offset,
            companyId,
            includeUnposted
        );
    },
    computeFormat: function (
        accountCodes,
        dateRange,
        offset = 0,
        companyId = null,
        includeUnposted = false
    ) {
        return this.getters.getCompanyCurrencyFormat(companyId && companyId.value) || "#,##0.00";
    },
});

functionRegistry.add("ODOO.BALANCE", {
    description: _lt("Get the total balance for the specified account(s) and period."),
    args: ODOO_FIN_ARGS(),
    returns: ["NUMBER"],
    compute: function (
        accountCodes,
        dateRange,
        offset = 0,
        companyId = null,
        includeUnposted = false
    ) {
        accountCodes = toString(accountCodes)
            .split(",")
            .map((code) => code.trim())
            .sort();
        offset = toNumber(offset);
        dateRange = parseAccountingDate(dateRange);
        includeUnposted = toBoolean(includeUnposted);
        return (
            this.getters.getAccountPrefixDebit(
                accountCodes,
                dateRange,
                offset,
                companyId,
                includeUnposted
            ) -
            this.getters.getAccountPrefixCredit(
                accountCodes,
                dateRange,
                offset,
                companyId,
                includeUnposted
            )
        );
    },
    computeFormat: function (
        accountCodes,
        dateRange,
        offset = 0,
        companyId = null,
        includeUnposted = false
    ) {
        return this.getters.getCompanyCurrencyFormat(companyId && companyId.value) || "#,##0.00";
    },
});

functionRegistry.add("ODOO.FISCALYEAR.START", {
    description: _lt("Returns the starting date of the fiscal year encompassing the provided date."),
    args: [
        arg("date (date)", _lt("Reference date.")),
        arg("company_id (number, optional)", _lt("The company.")),
    ],
    returns: ["NUMBER"],
    computeFormat: () => "m/d/yyyy",
    compute: function (date, companyId = null) {
        const startDate = this.getters.getFiscalStartDate(
            toJsDate(date),
            companyId === null ? null : toNumber(companyId)
        );
        return toNumber(startDate);
    },
});

functionRegistry.add("ODOO.FISCALYEAR.END", {
    description: _lt("Returns the ending date of the fiscal year encompassing the provided date."),
    args: [
        arg("date (date)", _lt("Reference date.")),
        arg("company_id (number, optional)", _lt("The company.")),
    ],
    returns: ["NUMBER"],
    computeFormat: () => "m/d/yyyy",
    compute: function (date, companyId = null) {
        const endDate = this.getters.getFiscalEndDate(
            toJsDate(date),
            companyId === null ? null : toNumber(companyId)
        );
        return toNumber(endDate);
    },
});

functionRegistry.add("ODOO.ACCOUNT.GROUP", {
    description: _lt("Returns the account ids of a given group."),
    args: [arg("type (string)", _lt("Account type."))],
    returns: ["NUMBER"],
    computeFormat: () => "m/d/yyyy",
    compute: function (accountType) {
        const accountTypes = this.getters.getAccountGroupCodes(toString(accountType));
        return accountTypes.join(",");
    },
});
