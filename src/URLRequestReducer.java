import java.io.IOException;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Reducer;

public class URLRequestReducer
        extends Reducer<Text, IntWritable, Text, IntWritable> {

    private final IntWritable result = new IntWritable();

    @Override
    protected void reduce(Text url, Iterable<IntWritable> values,
                          Context context)
            throws IOException, InterruptedException {

        int totalRequests = 0;

        for (IntWritable value : values) {
            totalRequests += value.get();
        }

        result.set(totalRequests);
        context.write(url, result);
    }
}
