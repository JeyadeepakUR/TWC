# High Level Architecture - Organization Management Service

![High Level Architecture](https://mermaid.ink/img/eyJjb2RlIjogImdyYXBoIFREXG4gICAgVXNlcltcIkNsaWVudCAvIEZyb250ZW5kXCJdXG4gICAgQWRtaW5bXCJPcmdhbml6YXRpb24gQWRtaW5cIl1cbiAgICBcbiAgICBzdWJncmFwaCBcIkFQSSBTZXJ2aWNlIChGYXN0QVBJKVwiXG4gICAgICAgIEF1dGhbXCJBdXRoIENvbnRyb2xsZXJcIl1cbiAgICAgICAgT3JnW1wiT3JnYW5pemF0aW9uIENvbnRyb2xsZXJcIl1cbiAgICAgICAgTWlkZGxld2FyZVtcIkpXVCBNaWRkbGV3YXJlXCJdXG5cbiAgICAgICAgc3ViZ3JhcGggXCJTZXJ2aWNlIExheWVyXCJcbiAgICAgICAgICAgIEF1dGhTZXJ2aWNlW1wiQXV0aCBTZXJ2aWNlXCJdXG4gICAgICAgICAgICBPcmdTZXJ2aWNlW1wiT3JnYW5pemF0aW9uIFNlcnZpY2VcIl1cbiAgICAgICAgZW5kXG4gICAgZW5kXG4gICAgXG4gICAgc3ViZ3JhcGggXCJEYXRhYmFzZSBMYXllciAoTW9uZ29EQilcIlxuICAgICAgICBNYXN0ZXJEQlsoXCJNYXN0ZXIgRGF0YWJhc2VcIildXG4gICAgICAgIE9yZ0NvbGwxWyhcIkNvbGxlY3Rpb246IG9yZ19BXCIpXVxuICAgICAgICBPcmdDb2xsMlsoXCJDb2xsZWN0aW9uOiBvcmdfQlwiKV1cbiAgICAgICAgT3JnQ29sbDNbKFwiQ29sbGVjdGlvbjogb3JnX0NcIildXG4gICAgZW5kXG5cbiAgICBVc2VyIC0tPnxcIlBPU1QgL29yZy9jcmVhdGVcInwgT3JnXG4gICAgT3JnIC0tPnxcIkNhbGwgU2VydmljZVwifCBPcmdTZXJ2aWNlXG4gICAgT3JnU2VydmljZSAtLT58XCJXcml0ZSBNZXRhZGF0YVwifCBNYXN0ZXJEQlxuICAgIE9yZ1NlcnZpY2UgLS0+fFwiQ3JlYXRlIENvbGxlY3Rpb25cInwgT3JnQ29sbDFcbiAgICBcbiAgICBBZG1pbiAtLT58XCJQT1NUIC9hZG1pbi9sb2dpblwifCBBdXRoXG4gICAgQXV0aCAtLT58XCJDYWxsIFNlcnZpY2VcInwgQXV0aFNlcnZpY2VcbiAgICBBdXRoU2VydmljZSAtLT58XCJWYWxpZGF0ZSBDcmVkZW50aWFsc1wifCBNYXN0ZXJEQlxuICAgIEF1dGhTZXJ2aWNlIC0tPnxcIlJldHVybiBKV1RcInwgQXV0aFxuICAgIEF1dGggLS0+fFwiUmVzcG9uc2VcInwgQWRtaW5cbiAgICBcbiAgICBBZG1pbiAtLT58XCJQVVQgL29yZy91cGRhdGUgKEJlYXJlciBUb2tlbilcInwgTWlkZGxld2FyZVxuICAgIE1pZGRsZXdhcmUgLS0+fFwiVmVyaWZ5IFRva2VuXCJ8IEF1dGhTZXJ2aWNlXG4gICAgTWlkZGxld2FyZSAtLT58XCJGb3J3YXJkIFJlcXVlc3RcInwgT3JnXG4gICAgT3JnIC0tPnxcIkNhbGwgU2VydmljZVwifCBPcmdTZXJ2aWNlXG4gICAgT3JnU2VydmljZSAtLT58XCJVcGRhdGUgTWV0YWRhdGFcInwgTWFzdGVyREJcbiAgICBPcmdTZXJ2aWNlIC0tPnxcIlJlbmFtZSBDb2xsZWN0aW9uXCJ8IE9yZ0NvbGwxIiwgIm1lcm1haWQiOiB7InRoZW1lIjogImRlZmF1bHQifX0=)

## Design Choices

1. **Framework**: FastAPI (Python)
   - High performance (Async/Await).
   - Automatic validation (Pydantic) and documentation (Swagger UI).

2. **Database**: MongoDB
   - **Schema-less**: Good for dynamic collections.
   - **Multi-tenancy Strategy**: **Collection-based isolation**. 
     - Each organization gets its own collection (`org_{name}`).
     - Metadata stored in `organizations` collection in Master DB.
     - Admin users stored in `admins` collection in Master DB.
   - **Trade-offs**: 
     - *Pros*: Logical separation, easy to manage 100s of tenants, single DB connection string.
     - *Cons*: Renaming collections can be heavy if data is huge (but `renameCollection` is fast metadata op in Mongo). Scalability limited by single Replica Set ultimately, but can shard by collection.

3. **Authentication**: JWT (JSON Web Tokens)
   - Stateless auth.
   - Embeds `org` identifier in token to avoid DB lookups for authorization on every request (though we check if org exists).

4. **Scalability**:
   - The service is stateless (containerize compliant).
   - MongoDB can be clustered.
   - Dynamic collections allow horizontal scaling strategies (sharding).

## Architecture Assessment

### Is this a good architecture?
**Yes, for a specific scale.** The **Collection-per-Tenant** strategy is a balanced approach for B2B SaaS applications where:
1.  **Data Isolation** is critical (tenants must not see each other's data).
2.  The number of tenants is moderate (thousands, not millions).
3.  Tenants have different schema needs (optional in Mongo).

### Scalability & Trade-offs

| Feature | Design Choice: Collection-per-Tenant | Trade-off / Limitation |
| :--- | :--- | :--- |
| **Isolation** | **High**. Data lives in `org_A`, `org_B`. Hard to accidentally leak data. | **Namespace Limit**. MongoDB has a limit on the number of namespaces (collections). Though high, millions of tenants would require sharding strategy adjustments. |
| **Performance** | **Good**. Queries are targeted to specific collections. Indices are smaller per-tenant. | **Resource Overhead**. Each collection has its own indexes, consuming RAM. Many small active collections can pressure the wiredTiger cache. |
| **Management** | **Easy CRUD**. deleting an org is just `dropCollection` (very fast). | **Cross-Tenant Reporting**. Aggregating data *across* all organizations (e.g., "Total Users Platform-wide") is very difficult and inefficient. |
| **Operations** | **Renaming**. We use `renameCollection`. | **Heavy Op**. Renaming a collection with GBs of data is resource-intensive and requires an exclusive lock. |

### Better Alternative Designs?

If we were designing for **Massive Scale (Millions of Tenants)**:

1.  **Single Collection with Tenant ID (Pooled)**:
    -   *Design*: All data in one `users` collection. Every document has `{ "org_id": "xyz", ... }`.
    -   *Pros*: Infinite scalability (sharding by `org_id`), efficient resource usage (shared indexes).
    -   *Cons*: Application logic must strictly enforce filter by `org_id` (Risk of data leaks). "Hard Delete" is slower (deleting millions of docs vs dropping 1 collection).

2.  **Hybrid Approach (Best of Both)**:
    -   **Tiered Storage**:
        -   **Free/Pro Tier**: Pooled (Single Collection) for thousands of small tenants. Cost-effective.
        -   **Enterprise Tier**: Dedicated Database/Collection for large tenants. Physical isolation and performance guarantees.

### Tech Stack Recommendation
-   **FastAPI**: Excellent choice. Async nature handles I/O bound database ops efficiently.
-   **MongoDB**: Great for dynamic schemas, but if the data is highly relational (e.g., complex billing, users in multiple orgs), **PostgreSQL** with Row-Level Security (RLS) might be safer and more robust for multi-tenancy.
