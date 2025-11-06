from state import informations


test = informations(highlights="Testd", full_description="full", includes=None, meeting_point="Barcelona", non_suitable=["older peopls"])
bana = informations(highlights=test.highlights, full_description="full", includes=None, meeting_point="Barcelona", non_suitable=["older peopls"])

print(bana)