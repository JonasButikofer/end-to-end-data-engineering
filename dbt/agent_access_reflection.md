# Agent Data Access Reflection

> Now that you've set up the dbt MCP server and seen an AI agent interact with your data models, take some time to think critically about what this means for data engineering. This reflection should be thoughtful (500-800 words), not a checklist.

As a note, I went the extra mile and exposed this to a Claude API MCP to get a better idea of what this can really do and have more experience with MCP. My reflection is based on that experience. 

---

## 1. What Worked Well

_Think about the experience of exposing your dbt models to an agent via MCP. What was effective? What surprised you about how the agent interacted with your data?_

I found that once I was able to connect and then have the agent visualize the whole process that I was able to immediately understand the architecture more easily than I did before. The way that it can look at everything and be the All-Seeing-Eye (with the list and get_lineage_dev tools) was amazing. I asked some other questions and got very clear responses as to where my documentation could be better; was that a failing on my part? Yes, but it also would make my life easier if this were in enterprise infrastructure because of the visibility of errors that I can now fix. I also used the MCP's build tool to run the tests tests and see the results in plain english. This gives insight to what needs to be fixed and the MCP can help dicipher the problem and help resolve it. The get_lineage tool also was incredibly helpful because I could ask about what would break if I changed part of the warehouse and get a clean answer that would normally take me over an hour to parse through. 

---

## 2. What Was Difficult or Confusing

_Where did the agent struggle? What required manual intervention or clarification? What parts of the setup were harder than expected?_

The agent understood the majority of my models. It began to have issues when I was asking about specific columns and what they all meant. That showed that I needed to update my documentation on some of the models. This shows that I will need to test everything before I release it to customers (internal or external) so that there are not ambiguity issues. An example was with the int_sales_orders_with_customers model where it had a filter for 30 days in the model but the documentation did not mention that. This means that the agent was trying to get records from it from all time but could not because of that filter. Adding the filters to the documentation is key because it affects the data outputs significantly. 

---

## 3. Documentation Quality

_You enhanced your dbt model and column descriptions to be "agent-friendly." Reflect on that process. What did you change? Why?_

I had to make the relationships between columns explicit because this did not have an ERD to see the relationships. Computers are also stupid and may attempt to join where there is no real relationship. When I had more explict relationships such as keys and what tables each model connected to, the agent had a much easier time getting me the data from more complex joins and relationships. This meant that when I explicitly added PK and FK information between the base_ecom__email_mktg_new and the stg_ecom__email_campaigns models (and CK as well if that had been applicable) there was less reasoning that the MCP had to do because it did not have to guess and look at lineage to be able to execute queries with the show tool. 

---

## 4. Production Considerations

_Imagine deploying this MCP server in a real company. What changes would be needed? What risks would you need to address?_

I would look for ways that this could be abused without setting up role based access. I would need to look for ways to set up roles and prevent jailbreaking the agent. These tools have a lot of access and making sure that no compliance regulations are broken and that the data stays protected is key. I would probably also want an internal flagging system that would prevent access when sensitive requests and pipeline modifications are attempted. Additionally, this is just a dbt MCP server. There are many kinds of MCPs that different users may find useful, such as a GitHub or database connecting MCP. This is just one agent and a real organization would need more than just this to leverage all of the value that agents can give. Finally, the agent does not leave a trail as far as I know and does not log who is using it. This means that without protections you could extract data and not know who did. That would need to be mitigated before it is deployed. This would include access to PII and sensitive data by agents which could pose a cybersecurity threat if the agent were compromised or if users of MCP agents are given more access then they should have. 

Another part is that I learned that it is not hard to run out of Snowflake or other warehouse computer if this is in the cloud. An agent is not aware of that. This could mean that there will be more compute cost than expected because of the access to data warehouses by everyone. 

---

## 5. Business Use Cases

_Based on what you've seen, describe 2-3 realistic business use cases where an agent with MCP access to a data warehouse could provide value._

The first would be natural language queries. Giving data access to less technical users would democratize the data warehouse, allowing for more data based decisions to less technical members of the organization that otherwise would need an analyst help retreive the data. Suppose that a marketing manager wants to know on the fly what the most effective marketing strategy was in the last campaign. They could easily ask that and have a response in seconds. Another way that I would use this would be to have it be the assistant in orienting new data team members on the warehouse. If I, as an engineer, did not need to tell you what each field is or where to find critical data, that would make all engineers more productive because you have the MCP that can access all of the documentation in seconds. I could also use MCP servers in triage to look at where there are breaks in the pipeline. If something broke it could take a long time to try and understand the changes and WHY the changes broke the whole system. This would reduce the time (and therefore the business cost) to getting a fix in the system. 

---

## 6. The Bigger Picture

_Data engineers have traditionally built pipelines that serve dashboards and reports. With agent access layers like MCP, data engineers are now also responsible for making data accessible to AI agents. How does this change the role?_

The job will become less focused on manual building and more strategic. There will be a lot more demand for Data AI Engineers who are able to get rich data and expose AI to that data. They will be in the job of getting those agents to everyone in an applicable role that will benefit from accessing data. Having everyone in an organization constantly connected to the data will allow those forward thinking organizations to work strategically because the knowledge that you need to pivot to follow the data, in any granular part of an organization, will be significantly cheaper to access. The domain and organizational knowledge that the data engineers have will soon be worth as much as the work that they do because writing the YAML for an agent to reach will be more important than writing SQL. 
