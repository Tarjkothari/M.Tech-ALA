public interface FeeCalculator {
/** Returns the total fee for the given course and number of credits. */
double calculate(String course, int credits);
}
