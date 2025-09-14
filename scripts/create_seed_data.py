import sys
import os
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from edu_register_api.core.database import SessionLocal
from edu_register_api.models import User, Item, Registration, Payment
from edu_register_api.enums import (
    ItemType,
    RegistrationStatus,
    PaymentMethod,
    PaymentStatus,
)
from edu_register_api.core.security import get_password_hash


def create_comprehensive_seed_data():
    session = SessionLocal()

    try:
        print("\n👥 테스트 사용자 생성 중...")
        users_data = [
            {"email": "not_used_user@example.com", "password": "password123"},
            {"email": "used_user@example.com", "password": "password123"},
        ]

        users = []
        for user_data in users_data:
            user = User(
                email=user_data["email"],
                hashed_password=get_password_hash(user_data["password"]),
            )
            session.add(user)
            users.append(user)

        session.flush()

        print("\n📚 과정 데이터 생성 중...")
        now = datetime.now(timezone.utc)

        courses_data = [
            {
                "title": "수강_기간_내_수업_1",
                "start_at": now - timedelta(days=6),
                "end_at": now + timedelta(days=10),
                "price": 299000,
                "created_at": now - timedelta(days=7),
            },
            {
                "title": "수강_기간_내_수업_2",
                "start_at": now - timedelta(days=4),
                "end_at": now + timedelta(days=44),
                "price": 199000,
                "created_at": now - timedelta(days=5),
            },
            {
                "title": "수강_기간_종료_수업_1",
                "start_at": now - timedelta(days=10),
                "end_at": now - timedelta(days=2),
                "price": 399000,
                "created_at": now - timedelta(days=10),
            },
            {
                "title": "수강_기간_도래_전_수업_1",
                "start_at": now + timedelta(days=2),
                "end_at": now + timedelta(days=51),
                "price": 399000,
                "created_at": now - timedelta(days=3),
            },
        ]

        courses = []
        for course_data in courses_data:
            course = Item(
                title=course_data["title"],
                item_type=ItemType.COURSE,
                start_at=course_data["start_at"],
                end_at=course_data["end_at"],
                created_at=course_data["created_at"],
            )
            session.add(course)
            courses.append(course)

        print("\n시험 데이터 생성 중...")
        tests_data = [
            {
                "title": "응시_기간_내_시험_1",
                "start_at": now - timedelta(days=7),
                "end_at": now + timedelta(days=5, hours=2),
                "price": 50000,
                "created_at": now - timedelta(days=7),
            },
            {
                "title": "응시_기간_종료_시험_1",
                "start_at": now - timedelta(days=6),
                "end_at": now + timedelta(days=12, hours=1, minutes=30),
                "price": 75000,
                "created_at": now - timedelta(days=6),
            },
            {
                "title": "응시_기간_도래_전_시험_1",
                "start_at": now + timedelta(days=1),
                "end_at": now + timedelta(days=30, hours=3),
                "price": 100000,
                "created_at": now - timedelta(days=1),
            },
        ]

        tests = []
        for test_data in tests_data:
            test = Item(
                title=test_data["title"],
                item_type=ItemType.TEST,
                start_at=test_data["start_at"],
                end_at=test_data["end_at"],
                created_at=test_data["created_at"],
            )
            session.add(test)
            tests.append(test)

        session.flush()

        print("\nRegistration 데이터 생성 중...")
        registrations = []
        reg_not_completed_course = Registration(
            user_id=users[0].id,
            item_id=courses[0].id,
            status=RegistrationStatus.PAID,
        )
        session.add(reg_not_completed_course)
        registrations.append(reg_not_completed_course)

        reg_completed_course = Registration(
            user_id=users[0].id,
            item_id=courses[2].id,
            status=RegistrationStatus.COMPLETED,
            completed_at=now - timedelta(days=2),
        )
        session.add(reg_completed_course)
        registrations.append(reg_completed_course)

        reg_completed_test = Registration(
            user_id=users[0].id,
            item_id=tests[1].id,
            status=RegistrationStatus.COMPLETED,
            completed_at=now - timedelta(days=1),
        )
        session.add(reg_completed_test)
        registrations.append(reg_completed_test)

        session.flush()

        print("\n결제내역 데이터 생성 중...")
        payments = []
        payment_not_completed_course = Payment(
            registration_id=reg_not_completed_course.id,
            amount=courses_data[0]["price"],
            status=PaymentStatus.PAID,
            method=PaymentMethod.CARD,
            paid_at=now - timedelta(days=5),
        )
        session.add(payment_not_completed_course)
        payments.append(payment_not_completed_course)

        payment_completed_course = Payment(
            registration_id=reg_completed_course.id,
            amount=courses_data[2]["price"],
            status=PaymentStatus.PAID,
            method=PaymentMethod.KAKAOPAY,
            paid_at=now - timedelta(days=3),
        )
        session.add(payment_completed_course)
        payments.append(payment_completed_course)

        payment_completed_test = Payment(
            registration_id=reg_completed_test.id,
            amount=tests_data[1]["price"],
            status=PaymentStatus.PAID,
            method=PaymentMethod.KAKAOPAY,
            paid_at=now - timedelta(days=1),
        )
        session.add(payment_completed_test)
        payments.append(payment_completed_test)

        session.commit()

        print("\n테스트 계정 정보:")
        print(f"{users_data[0]['email']} (비밀번호: {users_data[0]['password']})")
        print(f"{users_data[1]['email']} (비밀번호: {users_data[1]['password']})")

    except Exception as e:
        session.rollback()
        print(f"\n❌ 오류 발생: {e}")
        import traceback

        print(traceback.format_exc())
        raise
    finally:
        session.close()


def main():
    try:
        create_comprehensive_seed_data()
    except Exception as e:
        print(f"❌ seed 데이터 생성 실패: {e}")
        return


if __name__ == "__main__":
    main()
