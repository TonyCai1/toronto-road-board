import unittest

from app import create_app, load_restrictions


class RoadBoardTestCase(unittest.TestCase):
    def setUp(self):
        app = create_app()
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_saved_data_contains_full_closure_and_lane_restriction(self):
        restrictions = load_restrictions()

        self.assertEqual(len(restrictions), 2)
        descriptions = [item["DESCRIPTION"].lower() for item in restrictions]
        self.assertTrue(any("full closure" in text for text in descriptions))
        self.assertTrue(any("lane blocked" in text for text in descriptions))

    def test_page_shows_streets_dates_and_two_road_closed_badges(self):
        response = self.client.get("/")
        page = response.get_data(as_text=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Queen St E", page)
        self.assertIn("Feb 28, 2024", page)
        self.assertIn("Nov 30, 2027", page)
        self.assertIn("Avenue Rd", page)
        self.assertIn("Jun 10, 2024", page)
        self.assertIn("Dec 31, 2026", page)
        self.assertEqual(page.count('class="badge">Road closed</span>'), 1)
        self.assertEqual(page.count('class="badge">Lane restriction</span>'), 1)

    def test_cards_show_the_saved_restriction_scope(self):
        page = self.client.get("/").get_data(as_text=True)
        lane_card = page.split('data-object-id="2088"', 1)[1].split("</article>", 1)[0]
        closure_card = page.split('data-object-id="2099"', 1)[1].split("</article>", 1)[0]

        # Correct for the record whose source description says "Full closure".
        self.assertIn("Road closed", closure_card)
        self.assertIn("Full closure", closure_card)

        self.assertIn("Lane restriction", lane_card)
        self.assertNotIn("Road closed", lane_card)
        self.assertIn("lane blocked", lane_card)

    def test_badges_match_restriction_scope(self):
        page = self.client.get("/").get_data(as_text=True)

        def rendered_badge(object_id: int) -> str:
            card = page.split(f'data-object-id="{object_id}"', 1)[1].split(
                "</article>", 1
            )[0]
            return card.split('class="badge">', 1)[1].split("</span>", 1)[0]

        actual_badges = {
            "Avenue Rd (OBJECTID 2088)": rendered_badge(2088),
            "Queen St E (OBJECTID 2099)": rendered_badge(2099),
        }
        expected_badges = {
            "Avenue Rd (OBJECTID 2088)": "Lane restriction",
            "Queen St E (OBJECTID 2099)": "Road closed",
        }

        self.assertEqual(actual_badges, expected_badges)


if __name__ == "__main__":
    unittest.main()
