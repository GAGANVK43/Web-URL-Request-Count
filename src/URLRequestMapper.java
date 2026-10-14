import java.io.IOException;
import org.apache.hadoop.io.IntWritable;
import org.apache.hadoop.io.LongWritable;
import org.apache.hadoop.io.Text;
import org.apache.hadoop.mapreduce.Mapper;

public class URLRequestMapper
        extends Mapper<LongWritable, Text, Text, IntWritable> {

    private final Text urlKey = new Text();
    private static final IntWritable ONE = new IntWritable(1);

    @Override
    protected void map(LongWritable key, Text value, Context context)
            throws IOException, InterruptedException {

        String line = value.toString();

        // Skip the CSV header
        if (line.startsWith("timestamp,")) {
            return;
        }

        String[] fields = line.split(",", -1);

        // CSV columns: timestamp, ip, method, url, status
        if (fields.length >= 5) {
            String url = fields[3].trim();

            if (!url.isEmpty()) {
                urlKey.set(url);
                context.write(urlKey, ONE);
            }
        }
    }
}
