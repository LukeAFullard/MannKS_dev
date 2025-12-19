# A Guide to Core Concepts in MannKenSen

Welcome to the `MannKenSen` package! To use it effectively, it's helpful to understand a few core concepts about how the package expects you to structure your data. This guide explains the two most important inputs: the **data vector (`x`)** and the **time vector (`t`)**.

---

### The Two Fundamental Inputs: `x` and `t`

Every major test function in this library (`trend_test`, `seasonal_trend_test`, etc.) requires two primary inputs:

1.  `x`: A vector representing your **measurements** or **observations**.
2.  `t`: A vector representing the **time** at which each measurement was taken.

These two vectors must correspond one-to-one. The first value in `x` was measured at the first time in `t`, the second value in `x` at the second time in `t`, and so on.

### Understanding the Data Vector (`x`)

The `x` vector contains the actual values you want to analyze for a trend.

-   **Data Type:** It can be a simple list or NumPy array of numbers (e.g., `[10, 12, 11.5, ...]`).
-   **Handling Censored Data:** One of the key features of `MannKenSen` is its ability to handle censored data. To use this, your `x` vector can contain a mix of numbers and **strings** representing censored values (e.g., `[10, '<12', 11.5, '>20']`).
-   **The `prepare_censored_data` Function:** Because the statistical functions cannot work with strings directly, you **must** pre-process any data vector containing censored strings. The `prepare_censored_data()` utility is designed for this. It converts your mixed-type array into a structured pandas DataFrame that the test functions understand.

**In summary: The `x` vector is where you put your measurements, and if those measurements include censored strings, you must use `prepare_censored_data()` first.**

---

### Understanding the Time Vector (`t`)

The `t` vector contains the timestamps for your measurements. Unlike the data vector, the time vector has stricter data type requirements.

-   **Recommended Data Type: `datetime` Objects**
    -   The **best and most recommended** format for your `t` vector is an array of Python `datetime` or pandas `Timestamp` objects.
    -   **Why?** The `MannKenSen` package is designed to leverage the rich information inside `datetime` objects. When you provide datetimes, the package can automatically figure out the month, day of the week, week of the year, etc. This is essential for seasonal analysis. The package also uses the precise nature of datetimes to correctly calculate the time difference between any two points, which is critical for handling unequally spaced data.

-   **Alternative Data Type: Numeric**
    -   You can also provide a numeric array for the `t` vector (e.g., `[2000.5, 2001.25, 2002.0]`).
    -   **When to use this:** This is appropriate if your time data is already in a consistent numeric format, like decimal years.
    -   **Limitation:** When using numeric time for a seasonal test, you lose the automatic seasonal detection. You must manually specify the `period` of your data (e.g., `period=12` for monthly data represented numerically).

-   **Why You Cannot Use Strings for Time**
    -   You **cannot** provide a vector of time strings (e.g., `['2000-06-30', '2001-03-31']`).
    -   The package cannot perform the necessary time-based calculations or seasonal groupings on plain strings. If your times are in string format, you must convert them to `datetime` objects before passing them to the `MannKenSen` functions. The `pandas.to_datetime()` function is excellent for this.

**In summary: The `t` vector is for time. Always use `datetime` objects for best results, especially for seasonal analysis. Convert any time strings to datetimes before you begin.**
