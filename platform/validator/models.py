import uuid

from django.db import models


class IdeaSubmission(models.Model):
    VERDICT_CHOICES = [
        ("build_now", "Build Now"),
        ("strong_foundation", "Strong Foundation"),
        ("refine_first", "Refine First"),
        ("validate_harder", "Validate Harder"),
        ("wrong_market", "Wrong Market"),
    ]

    uid = models.UUIDField(default=uuid.uuid4, unique=True, db_index=True)
    email = models.EmailField(db_index=True)
    idea_name = models.CharField(max_length=200)
    idea_description = models.TextField()
    target_market = models.CharField(max_length=300)
    problem_solved = models.TextField()

    score = models.PositiveSmallIntegerField(null=True, blank=True)
    verdict = models.CharField(max_length=30, choices=VERDICT_CHOICES, blank=True)
    headline = models.CharField(max_length=400, blank=True)
    basic_analysis = models.TextField(blank=True)
    deep_data = models.JSONField(null=True, blank=True)

    is_paid = models.BooleanField(default=False)
    paystack_ref = models.CharField(max_length=100, blank=True, db_index=True)
    analysis_done = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Idea Submission"
        verbose_name_plural = "Idea Submissions"

    def __str__(self):
        return f"{self.idea_name} ({self.email})"

    @property
    def verdict_label(self):
        return dict(self.VERDICT_CHOICES).get(self.verdict, "")

    @property
    def score_color(self):
        if not self.score:
            return "#6b6b68"
        if self.score >= 7:
            return "#22c55e"
        if self.score >= 5:
            return "#e89240"
        return "#ef4444"

    @property
    def verdict_color(self):
        green = {"build_now", "strong_foundation"}
        red = {"wrong_market"}
        if self.verdict in green:
            return "#22c55e"
        if self.verdict in red:
            return "#ef4444"
        return "#e89240"
