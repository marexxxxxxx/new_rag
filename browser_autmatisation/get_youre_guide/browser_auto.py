from browser_use import Agent, ChatOllama


task = """

1. Go to https://www.getyourguide.com/
2. Take a screenshot of the page.
3. Wait 2 seconds.
4. Use find_text to locate the 'I agree' button (cookie acceptance).
5. Take a screenshot before clicking.
6. Click the 'I agree' button.
7. Wait 2 seconds.
8. Take a screenshot after click.
9. Use find_text to find the element labeled 'Find places and things to do'.
10. Take a screenshot before clicking.
11. Click this element.
12. Wait 2 seconds.
13. Take a screenshot after click.
14. Use send_keys to type 'Fuerteventura' in the search bar.
15. Take a screenshot after typing.
16. Wait 1 second.
17. Use find_text to find the button labeled 'Anytime'.
18. Take a screenshot before clicking.
19. Click the 'Anytime' button.
20. Wait 1 second.
21. Take a screenshot after click.
22. Use find_text to locate the date selector for '28 October'.
23. Take a screenshot before clicking.
24. Click '28 October'.
25. Wait 1 second.
26. Take a screenshot after click.
27. Use find_text to locate the date selector for '30 October'.
28. Take a screenshot before clicking.
29. Click '30 October'.
30. Wait 1 second.
31. Take a screenshot after click.
32. (Optional: If only '29 October' is available instead, select '29 October' and take a screenshot.)
33. Use find_text to find the 'Search' button.
34. Take a screenshot before clicking.
35. Click 'Search'.
36. Wait 3 seconds for results to load.
37. Take a screenshot of the results page.
38. Extract the results page link and return it.
39. If any step fails, immediately take a screenshot and log the error before aborting.


"""




llm = ChatOllama(model="hf.co/unsloth/Apriel-1.5-15b-Thinker-GGUF:Q6_K")

agent = Agent(
    task=task,
    llm=llm
)

async def main():
    history = await agent.run()

import asyncio
asyncio.run(main())