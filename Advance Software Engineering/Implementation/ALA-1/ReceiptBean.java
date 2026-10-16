import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.Serializable;
public class ReceiptBean implements PropertyChangeListener, Serializable {
    private static final long serialVersionUID = 1L;
    private StudentBean student;
    public ReceiptBean() { }
    public void setStudent(StudentBean student) { this.student = student; }
    @Override
    public void propertyChange(PropertyChangeEvent e) {
        if ("fee".equals(e.getPropertyName())) {
            printReceipt((Double) e.getNewValue());
        }
    }
    private void printReceipt(double fee) {
        System.out.println("=========== FEE RECEIPT ===========");
        System.out.println("Student : " + student.getName());
        System.out.println("Course : " + student.getCourse());
        System.out.println("Credits : " + student.getCredits());
        System.out.println("Fee : Rs. " + fee);
        System.out.println("===================================");
    }
}