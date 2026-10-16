public class Main {
    public static void main(String[] args) {
        StudentBean student = new StudentBean();
        FeeCalculatorBean calculator = new FeeCalculatorBean();
        ReceiptBean receipt = new ReceiptBean();
        // wiring (composition) - components do not know each other's internals
        student.addPropertyChangeListener(calculator);
        calculator.addPropertyChangeListener(receipt);
        receipt.setStudent(student);
        student.setName("Student Name");
        student.setCourse("M.Tech CE");
        student.setCredits(5); // triggers fee calculation and receipt
    }
}