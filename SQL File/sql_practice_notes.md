# SQL Practice Notes

Warmup session covering `GROUP BY`, `HAVING`, subqueries, and `JOIN`s.

---

## Sample Tables Used

**employees**

| id | name | department | salary |
|----|------|------------|--------|
| 1 | Amit | Engineering | 75000 |
| 2 | Priya | Sales | 62000 |
| 3 | Rohan | Engineering | 81000 |
| 4 | Sneha | Marketing | 58000 |
| 5 | Vikram | Sales | 67000 |

**departments**

| dept_id | department | manager |
|---------|------------|---------|
| 1 | Engineering | Rohan |
| 2 | Sales | Vikram |
| 3 | Marketing | Sneha |

---

## Question 1: Average salary per department

**Task:** Find the average salary per department, sorted highest to lowest.

**My first attempt:**
```sql
Select department, salary From employees where Average(salary) Groupby department.
```

**Issues found:**
- `Average` is not valid — correct function is `AVG()`
- Aggregate functions (`AVG`, `SUM`, etc.) cannot be used in `WHERE` — they don't exist yet at that stage of query execution
- `GROUPBY` needs a space: `GROUP BY`
- Once grouping, `SELECT` can only include grouped columns or aggregates — not raw `salary`

**Correct solution:**
```sql
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
ORDER BY avg_salary DESC;
```

---

## Question 2: Departments with average salary > 65000

**My attempt:**
```sql
SELECT department FROM employees GROUPBY department Having AVG(salary)>65000 ;
```

**Issue:** `GROUPBY` → needs a space (`GROUP BY`). Everything else was correct.

**Correct solution:**
```sql
SELECT department 
FROM employees 
GROUP BY department 
HAVING AVG(salary) > 65000;
```

**Result:** Only **Engineering** qualifies (avg = 78000). Sales avg = 64500, which does not pass the >65000 condition.

---

## Question 3: Employee(s) with the highest salary

**My attempt:**
```sql
SELECT name FROM employees WHERE MAX(salary);
```

**Issue:** `MAX(salary)` returns a number, not a boolean — and aggregates can't go in `WHERE` directly. Needed a subquery instead.

**Correct solution:**
```sql
SELECT name 
FROM employees 
WHERE salary = (SELECT MAX(salary) FROM employees);
```

**How it works:**
1. Inner query `(SELECT MAX(salary) FROM employees)` runs first, returning the single max value.
2. Outer query filters for rows matching that value.

**Handling ties:** This approach correctly returns *all* employees who share the max salary (unlike `ORDER BY salary DESC LIMIT 1`, which would only return one row even in a tie).

---

## Question 4: Employee name + their department's manager

**Task:** List each employee's name along with the manager of their department, using a `JOIN`.

**Solution:**
```sql
SELECT e.name, d.manager
FROM employees e
JOIN departments d
ON e.department = d.department;
```

**How it works:**
- Joins `employees` (aliased `e`) with `departments` (aliased `d`) on matching `department` values.
- For each employee, pulls the `manager` from the matching department row.

**Expected output:**

| name | manager |
|------|---------|
| Amit | Rohan |
| Priya | Vikram |
| Rohan | Rohan |
| Sneha | Sneha |
| Vikram | Vikram |

---

## Question 5: Pairs of employees in the same department (self join)

**Task:** List every pair of employees who work in the same department, without listing the same pair twice or pairing an employee with themselves.

**My first attempt:**
```sql
SELECT e1.name, e2.name, e1.department
FROM employees e1
JOIN employees e2
ON e1.department = e2.department;
```

**Issues found:**
- With no extra condition, every employee matches themselves (`e1.name = e2.name`), producing useless self-pairs
- Each real pair also appears twice — once as (A, B) and once as (B, A)

**Correct solution:**
```sql
SELECT e1.name AS employee1, e2.name AS employee2, e1.department
FROM employees e1
JOIN employees e2
  ON e1.department = e2.department
  AND e1.id < e2.id;
```

**How it works:**
- This is a true self join: the `employees` table is joined to itself via two aliases, `e1` and `e2`.
- `e1.department = e2.department` matches employees in the same department.
- `e1.id < e2.id` keeps only one direction of each pair and excludes an employee matching itself.

**Expected output:**

| employee1 | employee2 | department |
|-----------|-----------|------------|
| Amit | Rohan | Engineering |
| Priya | Vikram | Sales |

**Note:** Sneha has no pair since she is the only employee in Marketing.

---

## Question 6: Employee with the second-highest salary

**Task:** Find the name and salary of the employee earning the second-highest salary.

**My first attempt:**
```sql
SELECT name, salary FROM employees WHERE salary = MAX(salary) - 1000;
```

**Issues found:**
- `MAX(salary)` still can't be used directly in `WHERE` — same problem as Question 3
- Subtracting a fixed amount (`- 1000`) only works if salaries happen to differ by exactly that much; it doesn't actually find the *second-highest*, just a guessed value

**Correct solution:**
```sql
SELECT name, salary
FROM employees
WHERE salary = (
    SELECT MAX(salary)
    FROM employees
    WHERE salary < (SELECT MAX(salary) FROM employees)
);
```

**How it works:**
1. Innermost subquery `(SELECT MAX(salary) FROM employees)` finds the overall highest salary (81000).
2. Middle subquery finds the highest salary among rows *below* that value — i.e. the second-highest (75000).
3. Outer query returns the employee(s) matching that salary.

**Expected output:**

| name | salary |
|------|--------|
| Amit | 75000 |

**Handling ties:** Like Question 3, this returns *every* employee at that salary level, and correctly skips ties for first place — if two employees tied for the highest salary, they'd both be excluded from the "second-highest" result, which is the standard definition of second-highest.

---

## Key Concepts Recap

| Clause | Purpose | Notes |
|--------|---------|-------|
| `WHERE` | Filters individual rows, before grouping | Cannot use aggregate functions |
| `GROUP BY` | Groups rows into buckets for aggregation | Enables per-group calculations like `AVG`, `SUM` |
| `HAVING` | Filters *groups* after aggregation | Think of it as `WHERE` for aggregated groups |
| Subquery | A query nested inside another query | Useful when filtering against an aggregate value |
| `JOIN` | Combines rows from two tables based on a related column | Different from a self join, which joins a table to itself |

**Order of SQL execution:** `FROM` → `WHERE` → `GROUP BY` → `HAVING` → `SELECT` → `ORDER BY`

**Self join clarification:** A self join is when a table is joined to itself (e.g., comparing employees to their managers when both are rows in the same `employees` table). Question 1 was *not* a self join — it only needed `GROUP BY`.
