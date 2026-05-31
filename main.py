import sys
import cv2

from src.config import CAMERA_CONFIG, ensure_directories
from src.ar.engine import AREngine
from src.utils import validate_image_path, validate_video_path
from src.camera.handler import list_available_cameras, open_camera


def main():
    print("=" * 50)
    print("AR Photo Player - MVP")
    print("=" * 50)

    ensure_directories()

    if len(sys.argv) >= 3:
        ref_image = sys.argv[1]
        video_file = sys.argv[2]
    else:
        ref_image = input("مسیر عکس مرجع: ").strip()
        video_file = input("مسیر ویدیو: ").strip()

    try:
        validate_image_path(ref_image)
        validate_video_path(video_file)
    except Exception as e:
        print(f"خطا: {e}")
        return

    cameras = list_available_cameras()
    if not cameras:
        print("دوربینی پیدا نشد!")
        return

    print(f"\nدوربین‌های موجود: {cameras}")

    ar_engine = None
    cap = None

    try:
        print("\nدر حال بارگذاری...")
        ar_engine = AREngine(ref_image, video_file)
        print("موتور AR آماده شد")
    except Exception as e:
        print(f"خطا در راه‌اندازی: {e}")
        return

    cap = open_camera()
    if cap is None:
        print("دوربین باز نشد!")
        if ar_engine:
            ar_engine.release()
        return

    print("\n" + "=" * 50)
    print("سیستم فعال شد!")
    print("عکس را جلوی دوربین بگیرید")
    print("برای خروج 'q' بزنید")
    print("برای نمایش آمار 's' بزنید")
    print("=" * 50 + "\n")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("خطا در خواندن فریم")
                break

            result, detected = ar_engine.process_frame(frame)
            cv2.imshow("AR Photo Player", result)

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):
                break
            elif key == ord("s"):
                stats = ar_engine.get_stats()
                print(f"\nآمار:")
                print(f"   کل فریم‌ها: {stats['total_frames']}")
                print(f"   فریم‌های تشخیص داده شده: {stats['detected_frames']}")
                print(f"   نرخ تشخیص: {stats['detection_rate']:.1f}%")
                print(f"   پیشرفت ویدیو: {stats['video_progress']:.1f}%\n")

    except KeyboardInterrupt:
        print("\nمتوقف شد")

    finally:
        cap.release()
        if ar_engine:
            ar_engine.release()
        cv2.destroyAllWindows()
        print("بسته شد")


if __name__ == "__main__":
    main()
