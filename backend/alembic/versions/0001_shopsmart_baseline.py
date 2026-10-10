"""ShopSmart Postgres baseline.

Replaces the legacy migration chain (archived under versions_legacy/) which
targeted the pre-ShopSmart schema. Creates all tables with Postgres-native
types: UUID PKs, JSONB documents, TIMESTAMPTZ stamps.

Revision ID: 0001_shopsmart_baseline
Revises: None (new baseline)
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB, UUID

revision = "0001_shopsmart_baseline"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("uuid", UUID(as_uuid=True), primary_key=True, default=sa.text("gen_random_uuid()")),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("hashed_password", sa.String(), nullable=False, server_default=""),
        sa.Column("salt", sa.String(), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("verification_token", sa.String(), nullable=True),
        sa.Column("email_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.PrimaryKeyConstraint("uuid"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.create_table(
        "categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("product_type", sa.String(), server_default=""),
        sa.Column("product_name", sa.String(), nullable=False),
        sa.Column("price", sa.Float(), nullable=False),
        sa.Column("sale_price", sa.Float(), nullable=True),
        sa.Column("blurb", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("brand", sa.String(), server_default=""),
        sa.Column("category", sa.String(), server_default="General"),
        sa.Column("original_price", sa.Float(), nullable=True),
        sa.Column("rating", sa.Float(), server_default="4.5"),
        sa.Column("review_count", sa.Integer(), server_default="0"),
        sa.Column("stock_count", sa.Integer(), server_default="10"),
        sa.Column("availability", sa.String(), server_default="IN_STOCK"),
        sa.Column("specs", JSONB(), server_default="{}"),
        sa.Column("ai_summary", JSONB(), server_default="{}"),
        sa.Column("tags", JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_products_slug", "products", ["slug"], unique=True)
    op.create_index("ix_products_brand", "products", ["brand"])
    op.create_index("ix_products_category", "products", ["category"])

    op.create_table(
        "product_categories",
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), primary_key=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("categories.id"), primary_key=True),
    )

    op.create_table(
        "product_sizes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("size", sa.String(), server_default=""),
        sa.Column("stock_quantity", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.uuid"), nullable=True),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("rating", sa.Integer(), nullable=False, server_default="5"),
    )
    op.create_index("ix_reviews_product_id", "reviews", ["product_id"])

    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.String(), nullable=False, server_default="guest"),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.uuid"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_carts_session_id", "carts", ["session_id"])

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cart_id", sa.Integer(), sa.ForeignKey("carts.id"), nullable=False),
        sa.Column("product_slug", sa.String(), sa.ForeignKey("products.slug"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("price", sa.Float(), nullable=False, server_default="0.0"),
    )
    op.create_index("ix_cart_items_cart_id", "cart_items", ["cart_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_number", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=True),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.uuid"), nullable=True),
        sa.Column("status", sa.String(), server_default="PROCESSING"),
        sa.Column("subtotal", sa.Float(), server_default="0.0"),
        sa.Column("shipping", sa.Float(), server_default="0.0"),
        sa.Column("tax", sa.Float(), server_default="0.0"),
        sa.Column("total", sa.Float(), server_default="0.0"),
        sa.Column("items", JSONB(), server_default="[]"),
        sa.Column("warehouse", sa.String(), server_default="East Coast Automated Fulfillment Center (Hub #4)"),
        sa.Column("carrier", sa.String(), server_default="ShopSmart AI Express Logistics"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_orders_order_number", "orders", ["order_number"], unique=True)
    op.create_index("ix_orders_session_id", "orders", ["session_id"])
    op.create_index("ix_orders_status", "orders", ["status"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), sa.ForeignKey("orders.id")),
        sa.Column("product_slug", sa.String(), sa.ForeignKey("products.slug"), nullable=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("price", sa.Float(), server_default="0.0"),
    )
    op.create_index("ix_order_items_order_id", "order_items", ["order_id"])

    op.create_table(
        "policy_documents",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("document", sa.String(), nullable=False),
        sa.Column("section", sa.String(), nullable=False, server_default=""),
        sa.Column("version", sa.String(), nullable=False, server_default="2026.1"),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("keywords", JSONB(), server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_policy_documents_document", "policy_documents", ["document"])

    op.create_table(
        "support_tickets",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ticket_number", sa.String(), nullable=False),
        sa.Column("subject", sa.String(), server_default=""),
        sa.Column("message", sa.Text(), server_default=""),
        sa.Column("status", sa.String(), server_default="OPEN"),
        sa.Column("email", sa.String(), server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_support_tickets_ticket_number", "support_tickets", ["ticket_number"], unique=True)
    op.create_index("ix_support_tickets_status", "support_tickets", ["status"])


def downgrade() -> None:
    for table in (
        "support_tickets",
        "policy_documents",
        "order_items",
        "orders",
        "cart_items",
        "carts",
        "reviews",
        "product_sizes",
        "product_categories",
        "products",
        "categories",
        "users",
    ):
        op.drop_table(table)
