# MURL API Field Glossary

Complete reference of all fields returned by the Jira Service Desk API for MURL requests.

## Request Metadata

| Field | API Path | Type | Description |
|-------|----------|------|-------------|
| Issue ID | `issueId` | string | Internal numeric ID (e.g. `513657`) |
| Issue Key | `issueKey` | string | Human-readable key (e.g. `MCML-1006`) |
| Request Type ID | `requestTypeId` | string | Always `321` for MURL requests |
| Service Desk ID | `serviceDeskId` | string | Service desk identifier |
| Created Date | `createdDate` | datetime | ISO 8601 timestamp of request creation |
| Friendly Date | `friendlyDate` | string | Human-readable date (e.g. `27/Nov/23 10:11 AM`) |
| Epoch Millis | `epochMillis` | number | Unix timestamp in milliseconds |

## Reporter

| Field | API Path | Type | Description |
|-------|----------|------|-------------|
| Reporter Name | `reporter.displayName` | string | Full name of the person who created the request |
| Reporter Email | `reporter.emailAddress` | string | Email address |
| Reporter Key | `reporter.key` | string | Internal user key |
| Reporter Active | `reporter.active` | boolean | Whether the user account is active |
| Reporter Timezone | `reporter.timeZone` | string | IANA timezone (e.g. `Europe/Zurich`) |

## Current Status

| Field | API Path | Type | Description |
|-------|----------|------|-------------|
| Status | `currentStatus.status` | string | Current workflow status (e.g. `Active`, `Pending Approval`) |
| Status Date | `currentStatus.statusDate` | datetime | When the status was last changed |

## Request Field Values (Custom Fields)

### Core MURL Fields

| Field | Field ID | Type | Description |
|-------|----------|------|-------------|
| MURL Name | `customfield_13721` | string | The MURL path/slug (e.g. `_digitalbanking-show/access-app-activation`) |
| Domain | `customfield_13707` | select | Target domain for the MURL |
| Purpose | `description` | text | Free-text description of what the MURL is for |
| Activation | `customfield_13702` | select | Activation status of the MURL |
| Create a Tiny Marketing URL | `customfield_14300` | select | Whether this is a tiny/short marketing URL |

### Target URLs

| Field | Field ID | Type | Description |
|-------|----------|------|-------------|
| Default Target URL | `customfield_13710` | url | Fallback target URL when no language match |
| Target German | `customfield_13711` | url | German-language target page |
| Target French | `customfield_13713` | url | French-language target page |
| Target Spanish | `customfield_13714` | url | Spanish-language target page |
| Target Portuguese | `customfield_13715` | url | Portuguese-language target page |
| Target Russian | `customfield_13716` | url | Russian-language target page |
| Target Japanese | `customfield_13717` | url | Japanese-language target page |
| Target Korean | `customfield_13718` | url | Korean-language target page |
| Target Dutch | `customfield_18001` | url | Dutch-language target page |
| Target Simplified Chinese | `customfield_13719` | url | Simplified Chinese target page |
| Target Traditional Chinese | `customfield_13720` | url | Traditional Chinese target page |

### People

| Field | Field ID | Type | Description |
|-------|----------|------|-------------|
| Requested For | `customfield_10603` | user | Person the MURL was requested for (may differ from reporter) |
| Owner 1 | `customfield_13705` | user | Primary owner responsible for the MURL |
| Owner 2 | `customfield_13706` | user | Secondary owner |
| Business Contact | `customfield_14301` | user | Business-side contact person |

### Organization

| Field | Field ID | Type | Description |
|-------|----------|------|-------------|
| Business Division | `customfield_10019` | select | Division that requested the MURL |
| Communication | `customfield_13722` | select | Communication channel (e.g. `Web`) |
| Region(s) | `customfield_13725` | select | Geographic region(s) the MURL targets |

### Properties & Configuration

| Field | Field ID | Type | Description |
|-------|----------|------|-------------|
| Language Selection | `customfield_13709` | select | Selected language(s) for the MURL |
| Properties | `customfield_13709` | multi-select | Properties like `Language-specific`, `Technical` |
| MURL Validity | `customfield_13724` | select | Validity period (e.g. `TLP`) |
| Due Date/Time | `customfield_13708` | datetime | Expiration or due date |

### Compliance

| Field | Field ID | Type | Description |
|-------|----------|------|-------------|
| Disclaimer | `customfield_10611` | select | General disclaimer confirmation |
| Data Protection Disclaimer | `customfield_13100` | select | Data protection terms confirmation |
| Records Management Disclaimer | `customfield_15101` | select | Records management terms confirmation |

## Notes

- User fields (`Owner 1`, `Owner 2`, `Requested For`, `Business Contact`) return nested objects with `displayName`, `emailAddress`, `key`, `active`, `timeZone`.
- Select fields return objects with `value` and sometimes `id`.
- Multi-select fields return arrays of value objects.
- Field IDs were identified from API response screenshots and need validation after first live run.
