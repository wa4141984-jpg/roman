                pd.DataFrame([dict(row) for row in orders]),
                use_container_width=True, hide_index=True
            )
            order_map = {f"Order #{row['id']} — {row['customer']}": row for row in orders}
            selected_order_label = st.selectbox("Select order to update", list(order_map.keys()))
            selected_order = order_map[selected_order_label]
            statuses = ["Received", "Preparing", "Ready", "Out for delivery", "Completed", "Cancelled"]
            status_index = statuses.index(selected_order["status"]) if selected_order["status"] in statuses else 0
            new_status = st.selectbox("New status", statuses, index=status_index)
            if st.button("Update order status"):
                with get_connection() as conn:
                    conn.execute("UPDATE orders SET status=? WHERE id=?",
                                 (new_status, selected_order["id"]))
                st.success("Order status updated.")
                st.rerun()
            order_lines = fetch_all(
                "SELECT food_name, quantity, unit_price, line_total FROM order_items WHERE order_id=?",
                (selected_order["id"],),
            )
            st.write(f"Items in order #{selected_order['id']}")
            st.dataframe(pd.DataFrame([dict(row) for row in order_lines]),
                         use_container_width=True, hide_index=True)
        else:
            st.info("There are no orders yet.")

    with tabs[2]:
        st.subheader("Manage categories")
        with st.form("category_form"):
            category_name = st.text_input("New category name", max_chars=60)
            add_category = st.form_submit_button("Add category")
        if add_category:
            if len(category_name.strip()) < 2:
                st.error("Category name must contain at least two characters.")
            else:
                try:
                    with get_connection() as conn:
                        conn.execute("INSERT INTO categories(name) VALUES (?)",
                                     (category_name.strip(),))
                    st.success("Category added.")
                    st.rerun()
                except sqlite3.IntegrityError:
                    st.error("That category already exists.")
        st.write("Existing categories")
        category_rows = fetch_all(
            """SELECT c.id, c.name, COUNT(f.id) AS item_count
               FROM categories c LEFT JOIN food_items f ON f.category_id=c.id
               GROUP BY c.id ORDER BY c.name"""
        )
        for category in category_rows:
            left, right = st.columns([4, 1])
            left.write(f"**{category['name']}** — {category['item_count']} food item(s)")
            if right.button("Delete", key=f"delete_category_{category['id']}"):
                if category["item_count"] > 0:
                    st.error("Move or delete this category's food items before deleting it.")
                else:
                    with get_connection() as conn:
                        conn.execute("DELETE FROM categories WHERE id=?", (category["id"],))
                    st.rerun()

    with tabs[3]:
        st.subheader("Sales reports")
        report = fetch_all(
            """SELECT DATE(created_at) AS day, COUNT(*) AS orders, SUM(total) AS sales
               FROM orders GROUP BY DATE(created_at) ORDER BY day"""
        )
        if report:
            df = pd.DataFrame([dict(row) for row in report])
            total_sales = float(df["sales"].sum())
            st.metric("All-time sales", money(total_sales))
            st.metric("Total orders", int(df["orders"].sum()))
            fig = px.line(df, x="day", y="sales", markers=True, title="Daily sales")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Sales reports will appear after the first order.")


# -------------------------------- MAIN ------------------------------------

def main():
    init_database()

    st.sidebar.title("🍽️ TasteHub")
    st.sidebar.caption("AI-Powered Restaurant Management")
    page = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard", "Digital Menu", "Shopping Cart",
            "AI Recommendations", "AI Assistant", "Customer Feedback", "Admin Panel"
        ],
    )
    st.sidebar.divider()
    st.sidebar.caption("Prices are displayed in Pakistani Rupees (PKR).")
    st.sidebar.caption("AI features require a Gemini API key.")

    if page == "Dashboard":
        dashboard_page()
    elif page == "Digital Menu":
        menu_page()
    elif page == "Shopping Cart":
        cart_page()
    elif page == "AI Recommendations":
        ai_recommendation_page()
    elif page == "AI Assistant":
        ai_assistant_page()
    elif page == "Customer Feedback":
        feedback_page()
    elif page == "Admin Panel":
        admin_page()


if __name__ == "__main__":
    main()
# roman
