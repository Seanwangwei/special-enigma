# Product Requirements Document (PRD)

# Exam Result Email Automation

| Item | Value |
|------|-------|
| Product | Exam Result Email Automation |
| Version | 1.0 |
| Status | MVP Complete |
| Product Owner | Sean Wang |
| Target Platform | Windows Desktop |
| Primary Users | University Registrar Office Staff |

---

# 1. Executive Summary

Exam Result Email Automation is a Windows desktop application designed to automate the preparation and delivery of examination result notifications to university students.

Instead of manually preparing hundreds of personalized emails each semester, Registrar Office staff can import a spreadsheet exported from the Student Information System (SIS), review automatically generated emails, and safely deliver them using Microsoft Outlook.

The application aims to reduce repetitive administrative work, improve consistency, minimize human error, and provide a complete audit trail for every notification.

---

# 2. Problem Statement

During each examination period, Registrar Office staff manually perform tasks including:

- Exporting examination results
- Determining the correct notification template
- Personalizing emails
- Listing failed modules
- Informing students of reassessment opportunities
- Sending emails
- Recording delivery status

This process is:

- Time-consuming
- Repetitive
- Prone to human error
- Difficult to audit
- Stressful during peak examination periods

The objective of this project is to automate these repetitive tasks while maintaining human oversight before emails are sent.

---

# 3. Product Goals

The application shall:

- Reduce manual effort required to notify students.
- Ensure every student receives the correct email template.
- Eliminate copy-and-paste errors.
- Support university reassessment workflows.
- Allow staff to review emails before delivery.
- Produce a complete audit log.
- Be usable by non-technical administrative staff.

---

# 4. Target Users

## Primary Users

Registrar Office staff responsible for:

- Examination administration
- Student progression
- Reassessment administration
- Official student communications

---

## Secondary Users

University IT administrators responsible for:

- Deployment
- Configuration
- Support

---

# 5. User Journey

```text
Launch Application

↓

Select Excel Spreadsheet

↓

Validate Spreadsheet

↓

Generate Emails

↓

Preview Emails

↓

Choose Delivery Method

↓

Confirm Operation

↓

Generate Outlook Drafts
OR
Send Emails

↓

Review Results Summary

↓

Audit Log Saved
```

---

# 6. Functional Requirements

## FR-1 Import Student Data

The application shall allow users to import an Excel spreadsheet exported from the Student Information System.

Supported format:

- Microsoft Excel (.xlsx)

Required columns include:

- Student ID
- Surname
- First Name
- Module Code
- Module Name
- Assessment Format
- Attempt
- Pass Credits
- Stage Average
- Email Template
- Number of Failed Modules

---

## FR-2 Student Grouping

Multiple spreadsheet rows belonging to the same student shall be grouped into a single notification.

Example:

Student A

- Module 1
- Module 2
- Module 3

↓

One email

---

## FR-3 Template Selection

The application shall select the appropriate email template according to the "Email Template" column.

Supported templates include:

- Progression
- Reassessment
- Extenuating Circumstances (EC)

Template selection shall be automatic.

---

## FR-4 Email Generation

For every student, the application shall generate:

- Subject
- Recipient
- HTML body
- Module table (auto-generated or from DOCX table definition — see FR-4.1)
- Personalised greeting

---

## FR-4.1 Dynamic Table Population (Sprint 7)

When a DOCX template contains a table, the application shall treat the table as a data template and populate it with student module data from the Excel spreadsheet.

### Table Header Detection

The application shall automatically detect the first row of a DOCX table as the **header row**. Header row cells contain column names that map to Excel columns (by normalized, case-insensitive name matching).

### Data Row Generation

For each module row belonging to a student in the Excel file, the application shall generate a corresponding table data row. Values from Excel columns are placed under the matching table header column.

**Example:**

DOCX table header: `| Module Code | Module Name | Credits | Semester | Module Type |`

Student Wang Wei has 2 modules in Excel → 2 data rows generated:

```
| 32          | I love you  |         |          |             |
| 12          | I hate you  |         |          |             |
```

### Unmapped Columns

If a table header column has no matching Excel column, the cell is left empty. The table structure and styling defined in the DOCX are preserved.

### Module Identification

Module-level rows are identified by columns whose values change across rows for the same Student ID. Student-level columns (same value across all rows for a student — e.g., First Name, Surname) are available as inline `{{variables}}` in the surrounding paragraphs.

### Backward Compatibility

- The existing `{{module_table}}` special variable continues to work with its default 4-column output.
- Templates without tables behave exactly as before.
- The feature is additive — no existing template behaviour is changed.

---

## FR-5 Email Preview

Users shall be able to preview generated emails before delivery.

The preview shall display:

- Recipient
- Subject
- HTML rendering

---

## FR-6 Validation

Before email generation begins, the application shall validate:

- Required columns exist
- Required values are present
- Email addresses are valid
- Templates exist
- Duplicate records
- Missing configuration

Validation failures shall prevent processing.

---

## FR-7 Delivery Modes

The application shall support three delivery modes.

### Preview Only

Generate previews only.

No emails created.

---

### Create Outlook Drafts (Default)

Create draft emails in Outlook.

Registrar staff review drafts before sending.

This is the recommended production workflow.

---

### Send Immediately

Send emails directly.

Confirmation shall be required before execution.

---

## FR-8 Outlook Integration

The primary delivery mechanism shall be Microsoft Outlook Desktop.

The application shall:

- Create email items
- Populate subject
- Populate recipient
- Populate HTML body
- Add attachments
- Save draft or send

---

## FR-9 Audit Logging

Every operation shall be recorded.

The audit log shall include:

- Timestamp
- Student ID
- Recipient
- Template
- Delivery mode
- Status
- Error message (if applicable)

---

## FR-10 Background Processing

Bulk operations shall execute in the background.

The GUI shall remain responsive.

---

## FR-11 Results Summary

After completion, users shall see:

- Total students processed
- Success count
- Failure count
- Skipped count
- Log file location

---

# 7. Business Rules

## BR-1

One student receives one email.

---

## BR-2

One email may contain multiple failed modules.

---

## BR-3

Template selection is driven entirely by the spreadsheet.

No manual override is required.

---

## BR-4

Validation must complete successfully before email generation.

---

## BR-5

Preview is recommended before sending.

---

## BR-6

Outlook Draft mode is the default delivery mode.

This reduces the risk of accidental mass email delivery.

---

## BR-7

The application shall not modify the imported spreadsheet.

---

# 8. Non-functional Requirements

## Performance

The application should process several hundred students within a reasonable time while keeping the interface responsive.

---

## Reliability

Failure to send one email shall not terminate the entire batch.

---

## Maintainability

Business logic shall remain separated from GUI code.

---

## Testability

Core business logic shall be unit tested.

---

## Usability

The interface shall be suitable for administrative users with limited technical experience.

---

## Portability

Development may occur on macOS or Linux.

Production deployment targets Windows.

---

# 9. Out of Scope

The following are not included in the current MVP.

- Student Information System integration
- Database storage
- User authentication
- Template editor
- Email scheduling
- Microsoft Graph integration
- Exchange Online API
- Multi-user support

---

# 10. Success Criteria

The product is considered successful when Registrar Office staff can:

- Import a spreadsheet
- Automatically generate correct emails
- Review emails
- Create Outlook drafts
- Send notifications
- Produce an audit log

without developer assistance.

---

# 11. Future Enhancements

Potential future enhancements include:

- Shared mailbox selection
- Outlook account selection
- Microsoft Graph API support
- Exchange Online support
- Multi-language templates
- Email scheduling
- Automatic retry
- Duplicate email detection
- Rich reporting dashboard

---

# 12. Acceptance Criteria

The MVP shall be considered complete when:

- The application launches successfully.
- Excel files are imported successfully.
- Student records are grouped correctly.
- Correct templates are selected.
- HTML emails are generated.
- Email previews are available.
- Outlook drafts can be created.
- Emails can be sent.
- Audit logs are generated.
- Automated tests pass.
- The application can be packaged into a standalone Windows executable.

---

# 13. Document History

| Version | Date | Description |
|----------|------|-------------|
| 1.0 | July 2026 | Initial PRD created following completion of MVP (Sprints 1–3). |
