# import json
# from collections import defaultdict
#
# def extract_unique_values():
#     # Read the input JSON file
#     with open('amazonexcluve_data.json', 'r') as f:
#         data = json.load(f)
#
#     # Initialize sets to store unique values
#     master_seasons = set()
#     dept_divs = set()
#     categories = set()
#     subclasses = set()
#
#     # Extract unique values
#     for item in data:
#         fields = item.get('fields', {})
#         if 'master_season' in fields:
#             master_seasons.add(fields['master_season'])
#         if 'dept_div' in fields:
#             dept_divs.add(fields['dept_div'])
#         if 'category' in fields:
#             categories.add(fields['category'])
#         if 'subclass' in fields:
#             subclasses.add(fields['subclass'])
#
#     # Convert sets to sorted lists for consistent ordering
#     master_seasons = sorted(list(master_seasons))
#     dept_divs = sorted(list(dept_divs))
#     categories = sorted(list(categories))
#     subclasses = sorted(list(subclasses))
#
#     # Save to JSON files
#     with open('mter_seasons.json', 'w') as f:
#         json.dump([{"name": name} for name in master_seasons], f, indent=2)
#
#     with open('de_divs.json', 'w') as f:
#         json.dump([{"name": name} for name in dept_divs], f, indent=2)
#
#     with open('categoes.json', 'w') as f:
#         json.dump([{"name": name} for name in categories], f, indent=2)
#
#     with open('subasses.json', 'w') as f:
#         json.dump([{"name": name} for name in subclasses], f, indent=2)
#
#     print(f"Extracted {len(master_seasons)} unique master seasons")
#     print(f"Extracted {len(dept_divs)} unique department divisions")
#     print(f"Extracted {len(categories)} unique categories")
#     print(f"Extracted {len(subclasses)} unique subclasses")
#
# if __name__ == "__main__":
#     extract_unique_values()

# import json
#
# # ✅ Utility function to load mapping from name → pk
# def load_mapping(file_path):
#     with open(file_path) as f:
#         data = json.load(f)
#     return {entry["fields"]["name"]: entry["pk"] for entry in data}
#
# # ✅ Load mappings from reference files
# master_season_map = load_mapping("MasterSeason.json")
# dept_div_map = load_mapping("DepartmentDivision.json")
# category_map = load_mapping("Category.json")
# subclass_map = load_mapping("Subclass.json")
#
# # ✅ Load AmazonExclusive data
# with open("amazonexcive_data.json") as f:
#     amazon_data = json.load(f)
#
# # ✅ Replace foreign key names with primary key values
# for entry in amazon_data:
#     fields = entry["fields"]
#
#     fields["master_season"] = master_season_map.get(fields["master_season"])
#     fields["dept_div"] = dept_div_map.get(fields["dept_div"])
#     fields["category"] = category_map.get(fields["category"])
#     fields["subclass"] = subclass_map.get(fields["subclass"])
#
#     # Optional: catch any missing mappings
#     if None in [fields["master_season"], fields["dept_div"], fields["category"], fields["subclass"]]:
#         print(f"⚠️ Missing FK mapping in entry: {entry}")
#
# # ✅ Save the cleaned file
# with open("amazonexclusive_data_cleaned.json", "w") as f:
#     json.dump(amazon_data, f, indent=2)

# print("✅ Cleaned data saved to amazonexclusive_data_cleaned.json")


# import json
# import os
# import django
# from datetime import datetime
#
# # Setup Django environment
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
# django.setup()
#
# from AmazoneMapApp.models import AmazonExclusive
#
# # Load JSON file
# with open("amazonexclusive_data_cleaned.json", "r") as f:
#     data = json.load(f)
#
# objects = []
# for item in data:
#     fields = item["fields"]
#
#     try:
#         obj = AmazonExclusive(
#             id=item["pk"],  # Optional: preserve primary key
#             master_season_id=fields["master_season"],
#             dept_div_id=fields["dept_div"],
#             category_id=fields["category"],
#             subclass_id=fields["subclass"],
#             created_at=datetime.fromisoformat(fields["created_at"].replace("Z", "+00:00")),
#             updated_at=datetime.fromisoformat(fields["updated_at"].replace("Z", "+00:00")),
#             is_active=fields["is_active"],
#             article_color_name=fields["article_color_name"],
#             year=fields["year"],
#             style_number=fields["style_number"],
#             style_desc=fields["style_desc"],
#             color_desc=fields["color_desc"],
#             size_desc=fields["size_desc"],
#             multipack_qty=fields["multipack_qty"],
#             variant_number=fields["variant_number"],
#             upc=str(fields["upc"]),
#             asin=fields["asin"],
#             current_status=fields["current_status"],
#             list_price=fields["list_price"],
#             planned_discount=fields["planned_discount"],
#             planned_asp=fields["planned_asp"],
#             merch_like_styles=fields["merch_like_styles"],
#         )
#         objects.append(obj)
#
#     except Exception as e:
#         print(f"⚠️ Skipping record with pk={item.get('pk')} due to error: {e}")
#
# # OPTIONAL: delete existing data if you're replacing it
# # AmazonExclusive.objects.all().delete()
#
# # Bulk create in batches
# batch_size = 1000
# total = len(objects)
# print(f"🚀 Inserting {total} records in batches of {batch_size}...")
#
# for i in range(0, total, batch_size):
#     AmazonExclusive.objects.bulk_create(objects[i:i+batch_size], batch_size=batch_size)
#     print(f"✅ Inserted records {i} to {min(i+batch_size, total)}")
#
# print("🎉 All records inserted successfully.")
