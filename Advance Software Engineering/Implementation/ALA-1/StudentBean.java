import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.io.Serializable;
public class StudentBean implements Serializable {
    private static final long serialVersionUID = 1L;
    private String name = "Tarj Kothari";
    private String course = "Computer Engineering";
    private int credits;
    private final PropertyChangeSupport pcs = new PropertyChangeSupport(this);
    public StudentBean() { } // public no-arg constructor
    public String getName() { return name; }
    public void setName(String name) {
        String old = this.name;
        this.name = name;
        pcs.firePropertyChange("name", old, name);
    }
    public String getCourse() { return course; }
    public void setCourse(String course) {
        String old = this.course;
        this.course = course;
        pcs.firePropertyChange("course", old, course); // bound property
    }
    public int getCredits() { return credits; }
    public void setCredits(int credits) {
        int old = this.credits;
        this.credits = credits;
        pcs.firePropertyChange("credits", old, credits); // bound property
    }
    public void addPropertyChangeListener(PropertyChangeListener l) { pcs.addPropertyChangeListener(l); }
    public void removePropertyChangeListener(PropertyChangeListener l) { pcs.removePropertyChangeListener(l); }
}