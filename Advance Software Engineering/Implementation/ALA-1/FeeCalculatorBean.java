import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.beans.PropertyChangeSupport;
import java.io.Serializable;
public class FeeCalculatorBean implements FeeCalculator, PropertyChangeListener, Serializable {
    private static final long serialVersionUID = 1L;
    private double fee;
    private final PropertyChangeSupport pcs = new PropertyChangeSupport(this);
    public FeeCalculatorBean() { }
    @Override
    public double calculate(String course, int credits) {
        double ratePerCredit = "M.Tech CE".equals(course) ? 4000.0 : 3500.0;
        return ratePerCredit * credits;
    }
    /** Required interface: reacts to changes in StudentBean. */
    @Override
    public void propertyChange(PropertyChangeEvent e) {
        String p = e.getPropertyName();
        if ("course".equals(p) || "credits".equals(p)) {
            StudentBean s = (StudentBean) e.getSource();
            setFee(calculate(s.getCourse(), s.getCredits()));
        }
    }
    /*Advance Software Engineering - METCE11501 Page 4*/
    public double getFee() { return fee; }
    public void setFee(double newFee) {
        double old = this.fee;
        this.fee = newFee;
        pcs.firePropertyChange("fee", old, newFee); // notifies ReceiptBean
    }
    public void addPropertyChangeListener(PropertyChangeListener l) { pcs.addPropertyChangeListener(l); }
    public void removePropertyChangeListener(PropertyChangeListener l) { pcs.removePropertyChangeListener(l); }
}