"""Import all models here so Alembic's autogenerate and Base.metadata see them."""
from app.models.user import (  # noqa: F401
    Role,
    User,
    UserProfile,
    RefreshToken,
    PasswordReset,
    EmailVerification,
)
from app.models.challenge import (  # noqa: F401
    ChallengeCategory,
    Challenge,
    ChallengeSession,
    ChallengeSubmission,
    ApiChallenge,
    SecurityChallenge,
    PerformanceChallenge,
    TestCase,
)
from app.models.bug import Bug, BugComment, BugAttachment  # noqa: F401
from app.models.xp import XpTransaction  # noqa: F401
from app.models.gamification import (  # noqa: F401
    Achievement,
    UserAchievement,
    Leaderboard,
)
from app.models.misc import (  # noqa: F401
    Notification,
    ActivityLog,
    AuditLog,
    DeveloperReview,
)
