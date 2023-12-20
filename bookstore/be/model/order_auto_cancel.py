import threading
from datetime import datetime, timedelta
from be.model import error, db_conn
from be.model.store import NewOrder as NewOrderModel


class OrderAutoCancel(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
        self.cancel_timer = threading.Timer(60, self.cancel_unpaid_orders)  # Timer executes every minute
        print('First start')
        self.cancel_timer.start()

    def cancel_unpaid_orders(self):
        try:
            current_time = datetime.now()
            time_interval = current_time - timedelta(minutes=1)

            unpaid_orders = (
                self.conn.query(NewOrderModel)
                .filter(NewOrderModel.status == 'unpaid', NewOrderModel.created_at < time_interval)
                .all()
            )

            for order in unpaid_orders:
                order.status = 'cancelled'
                self.conn.commit()

        except Exception as e:
            print(f"Error canceling unpaid orders: {str(e)}")

        # Restart the timer
        self.cancel_timer = threading.Timer(60, self.cancel_unpaid_orders)
        print('Second start')
        self.cancel_timer.start()


if __name__ == "__main__":
    order_auto_cancel = OrderAutoCancel()
