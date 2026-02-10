import unittest

from backend.core.context import NormalizedLearningContext, build_normalized_context
from backend.core.student_profile import StudentProfileValidationError
from backend.services.request_router import handle_tutor_request
from backend.services.tutor_response_service import InvalidContextError, build_response_prompt


class LearningContextTests(unittest.TestCase):
    def setUp(self):
        self.valid_payload = {
            "class_level": "Class 7",
            "board": "CBSE",
            "subject": "Math",
            "chapter": "Fractions",
            "proficiency": "beginner",
            "question": "What is a proper fraction?",
        }

    def test_missing_required_fields_are_rejected(self):
        invalid_payload = {k: v for k, v in self.valid_payload.items() if k != "board"}

        with self.assertRaises(StudentProfileValidationError):
            build_normalized_context(invalid_payload)

    def test_normalized_context_contains_profile_and_pedagogy(self):
        context = build_normalized_context(self.valid_payload)

        self.assertIsInstance(context, NormalizedLearningContext)
        self.assertEqual(context.student_profile.proficiency, "beginner")
        self.assertEqual(context.pedagogy.explanation_style, "story-based")
        self.assertGreaterEqual(context.pedagogy.allowed_examples_count, 1)

    def test_downstream_layer_requires_normalized_context(self):
        with self.assertRaises(InvalidContextError):
            build_response_prompt("Explain", context={})  # type: ignore[arg-type]

    def test_request_router_sends_normalized_constraints_to_downstream(self):
        prompt = handle_tutor_request(self.valid_payload)

        self.assertIn("Keep answer <=", prompt)
        self.assertIn("at most", prompt)
        self.assertIn("Fractions", prompt)


if __name__ == "__main__":
    unittest.main()
