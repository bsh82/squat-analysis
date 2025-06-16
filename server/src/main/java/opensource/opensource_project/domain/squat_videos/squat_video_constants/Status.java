package opensource.opensource_project.domain.squat_videos.squat_video_constants;

public enum Status {
    DONE("done"),
    FAILED("failed");

    private final String value;

    Status(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
