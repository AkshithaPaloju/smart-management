import streamlit as st
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError
from typing import Optional
import requests

# Load environment variables
load_dotenv()

# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Smart Donation Matcher",
    page_icon="🤝",
    layout="wide"
)

# -----------------------------
# Pydantic Models
# -----------------------------
class Donation(BaseModel):
    donor_name: str
    item_name: str
    category: str
    quantity: int
    location: str
    condition: str
    description: Optional[str] = ""


class Requirement(BaseModel):
    organization_name: str
    required_item: str
    category: str
    quantity_needed: int
    location: str
    urgency: str


# -----------------------------
# Session State
# -----------------------------
if "donations" not in st.session_state:
    st.session_state.donations = []

if "requirements" not in st.session_state:
    st.session_state.requirements = []


# -----------------------------
# Title
# -----------------------------
st.title("🤝 Smart Donation Item Matching Platform")

st.write(
    "Connect donated items with organizations or people who need them."
)

st.divider()


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("📌 Navigation")

page = st.sidebar.radio(
    "Choose an option:",
    [
        "🏠 Home",
        "🎁 Add Donation",
        "📋 Add Requirement",
        "🔍 Find Matches",
        "📊 Dashboard"
    ]
)


# =========================================================
# HOME
# =========================================================

if page == "🏠 Home":

    st.header("Welcome to Smart Donation Matching")

    st.write("""
    This platform helps donors find suitable recipients for their
    donated items.

    Instead of manually searching for organizations, the platform
    compares donation details with requirements and suggests the
    best available matches.
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🎁 Donate")
        st.write(
            "Add details about clothes, books, food, electronics "
            "or other useful items."
        )

    with col2:
        st.subheader("📋 Request")
        st.write(
            "Organizations can add the items and quantities they need."
        )

    with col3:
        st.subheader("🔍 Match")
        st.write(
            "The system compares donations with requirements and "
            "provides suitable matches."
        )

    st.divider()

    st.info(
        "💡 Start by adding a donation or a requirement using the sidebar."
    )


# =========================================================
# ADD DONATION
# =========================================================

elif page == "🎁 Add Donation":

    st.header("🎁 Add Donation")

    with st.form("donation_form"):

        donor_name = st.text_input("Donor Name")

        item_name = st.text_input(
            "Item Name",
            placeholder="Example: School Books"
        )

        category = st.selectbox(
            "Category",
            [
                "Clothes",
                "Books",
                "Food",
                "Electronics",
                "Furniture",
                "Medical Supplies",
                "Toys",
                "Other"
            ]
        )

        quantity = st.number_input(
            "Quantity",
            min_value=1,
            value=1,
            step=1
        )

        location = st.text_input(
            "Location",
            placeholder="Example: Hyderabad"
        )

        condition = st.selectbox(
            "Condition",
            [
                "New",
                "Like New",
                "Good",
                "Used"
            ]
        )

        description = st.text_area(
            "Description",
            placeholder="Enter additional information..."
        )

        submit = st.form_submit_button(
            "➕ Add Donation"
        )

    if submit:

        try:

            donation = Donation(
                donor_name=donor_name,
                item_name=item_name,
                category=category,
                quantity=quantity,
                location=location,
                condition=condition,
                description=description
            )

            st.session_state.donations.append(
                donation.model_dump()
            )

            st.success(
                "✅ Donation added successfully!"
            )

        except ValidationError as error:

            st.error(
                "Please provide valid donation details."
            )


# =========================================================
# ADD REQUIREMENT
# =========================================================

elif page == "📋 Add Requirement":

    st.header("📋 Add Item Requirement")

    with st.form("requirement_form"):

        organization_name = st.text_input(
            "Organization / Recipient Name"
        )

        required_item = st.text_input(
            "Required Item",
            placeholder="Example: School Books"
        )

        category = st.selectbox(
            "Category",
            [
                "Clothes",
                "Books",
                "Food",
                "Electronics",
                "Furniture",
                "Medical Supplies",
                "Toys",
                "Other"
            ]
        )

        quantity_needed = st.number_input(
            "Quantity Needed",
            min_value=1,
            value=1,
            step=1
        )

        location = st.text_input(
            "Location",
            placeholder="Example: Hyderabad"
        )

        urgency = st.selectbox(
            "Urgency",
            [
                "Low",
                "Medium",
                "High",
                "Emergency"
            ]
        )

        submit = st.form_submit_button(
            "➕ Add Requirement"
        )

    if submit:

        try:

            requirement = Requirement(
                organization_name=organization_name,
                required_item=required_item,
                category=category,
                quantity_needed=quantity_needed,
                location=location,
                urgency=urgency
            )

            st.session_state.requirements.append(
                requirement.model_dump()
            )

            st.success(
                "✅ Requirement added successfully!"
            )

        except ValidationError:

            st.error(
                "Please provide valid requirement details."
            )


# =========================================================
# FIND MATCHES
# =========================================================

elif page == "🔍 Find Matches":

    st.header("🔍 Smart Donation Matching")

    if not st.session_state.donations:

        st.warning(
            "⚠️ No donations available. Please add a donation first."
        )

    elif not st.session_state.requirements:

        st.warning(
            "⚠️ No requirements available. Please add a requirement first."
        )

    else:

        st.write(
            "The system compares donations and requirements "
            "using category, item name, location and quantity."
        )

        st.divider()

        match_found = False

        for donation in st.session_state.donations:

            for requirement in st.session_state.requirements:

                score = 0
                reasons = []

                # Category matching
                if donation["category"] == requirement["category"]:
                    score += 40
                    reasons.append("Category matches")

                # Item name matching
                donation_item = donation["item_name"].lower()
                required_item = requirement["required_item"].lower()

                if (
                    donation_item in required_item
                    or required_item in donation_item
                ):
                    score += 30
                    reasons.append("Item name matches")

                # Location matching
                donation_location = donation["location"].lower()
                requirement_location = requirement["location"].lower()

                if donation_location == requirement_location:
                    score += 20
                    reasons.append("Location matches")

                # Quantity matching
                if donation["quantity"] >= requirement["quantity_needed"]:
                    score += 10
                    reasons.append("Quantity is sufficient")

                # Display suitable match
                if score >= 50:

                    match_found = True

                    st.success(
                        f"🎯 Match Found — {score}% Match"
                    )

                    col1, col2 = st.columns(2)

                    with col1:

                        st.subheader("🎁 Donation")

                        st.write(
                            f"**Donor:** {donation['donor_name']}"
                        )

                        st.write(
                            f"**Item:** {donation['item_name']}"
                        )

                        st.write(
                            f"**Category:** {donation['category']}"
                        )

                        st.write(
                            f"**Quantity:** {donation['quantity']}"
                        )

                        st.write(
                            f"**Location:** {donation['location']}"
                        )

                        st.write(
                            f"**Condition:** {donation['condition']}"
                        )

                    with col2:

                        st.subheader("📋 Requirement")

                        st.write(
                            f"**Organization:** "
                            f"{requirement['organization_name']}"
                        )

                        st.write(
                            f"**Required Item:** "
                            f"{requirement['required_item']}"
                        )

                        st.write(
                            f"**Category:** "
                            f"{requirement['category']}"
                        )

                        st.write(
                            f"**Quantity Needed:** "
                            f"{requirement['quantity_needed']}"
                        )

                        st.write(
                            f"**Location:** "
                            f"{requirement['location']}"
                        )

                        st.write(
                            f"**Urgency:** "
                            f"{requirement['urgency']}"
                        )

                    st.write(
                        "**Matching Reasons:** "
                        + ", ".join(reasons)
                    )

                    st.divider()

        if not match_found:

            st.info(
                "❌ No suitable matches found yet."
            )


# =========================================================
# DASHBOARD
# =========================================================

elif page == "📊 Dashboard":

    st.header("📊 Donation Dashboard")

    total_donations = len(
        st.session_state.donations
    )

    total_requirements = len(
        st.session_state.requirements
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Total Donations",
            total_donations
        )

    with col2:

        st.metric(
            "Total Requirements",
            total_requirements
        )

    with col3:

        matched_count = 0

        for donation in st.session_state.donations:

            for requirement in st.session_state.requirements:

                if (
                    donation["category"]
                    == requirement["category"]
                ):

                    matched_count += 1

        st.metric(
            "Potential Matches",
            matched_count
        )

    st.divider()

    # Donations table
    if st.session_state.donations:

        st.subheader("🎁 Available Donations")

        st.dataframe(
            st.session_state.donations,
            use_container_width=True
        )

    # Requirements table
    if st.session_state.requirements:

        st.subheader("📋 Current Requirements")

        st.dataframe(
            st.session_state.requirements,
            use_container_width=True
        )


# =========================================================
# FOOTER
# =========================================================

st.sidebar.divider()

st.sidebar.caption(
    "🤝 Smart Donation Item Matching Platform"
)

st.sidebar.caption(
    "Built using Python + Streamlit"
)