ALERT_QUERY = """
    SELECT a.id, u.username, u.email, a.price, s.status,  u.first_name
    FROM alert a left join alert_status s on a.status_id=s.id
    left join user u on a.created_by_id = u.id
    where u.is_active=true and a.is_active=true and s.is_active=true and s.status="Created" and a.price = {current_price};
"""

UPDATE_ALERT_STATUS = """
update alert
set status_id = 2
where created_by_id in {username} and price = {price};
"""
