package utils.charts;

import java.awt.Color;

import org.jfree.chart.ChartFactory;
import org.jfree.chart.ChartPanel;
import org.jfree.chart.JFreeChart;
import org.jfree.chart.plot.PlotOrientation;
import org.jfree.data.category.DefaultCategoryDataset;
import org.jfree.ui.ApplicationFrame;


/**
 * ApplicationFrame is a wrapper over javax.swing.JFrame that implements
 * java.awt.event.WindowListener, provided by JFreeChart in order to
 * encapsulate GUI Window logic. This is where the plot will be drawn.
 * One can save the Plot to a file and zoom in/out of the Y axis.
 */
public final class LineChart <T> extends ApplicationFrame {
	private static final long serialVersionUID = 602433412432056535L;

	/* Values are null-allowed. */
	public LineChart(String window_title, String chart_title,
			         String xlabel, String ylabel,
			         Comparable<T> xvalues[], Number yvalues[]) {
		super(window_title);
		
		/* Build a dataset from x-data and y-data. */
		DefaultCategoryDataset dataset = new DefaultCategoryDataset();
		
		if (xvalues.length != yvalues.length) {
			System.err.println("xvalues and yvalues have different length!");
		}
		else {
			for (int i = 0; i < xvalues.length; i++) {
				dataset.addValue(yvalues[i], "", xvalues[i]);
			}
		}
	    
	    JFreeChart chart = ChartFactory.createLineChart(
	    		chart_title,
	    		xlabel,
	    		ylabel,
	    		dataset,
	    		PlotOrientation.VERTICAL,
	    		false,  /* legend */
	    		true,  /* ToolTips */
	    		false  /* URLs */
	    );
	    
	    /* A Swing GUI component for displaying a JFreeChart object. */
	    ChartPanel panel = new ChartPanel(chart, true, true, true, false, true);
	    panel.setMouseWheelEnabled(true);
	    panel.setMouseZoomable(true);
	    panel.setDomainZoomable(true);
	    panel.setRangeZoomable(true);
	    panel.setFillZoomRectangle(true);
	    panel.setBackground(Color.WHITE);
	    chart.getPlot().setBackgroundPaint(Color.WHITE);
	    
	    setContentPane(panel);
	}
	
	public LineChart(Comparable<T> xvalues[], Number yvalues[]) {
		this(null, null, null, null, xvalues, yvalues);
	}
	
	public void display() {
		this.pack();  // Resize the window to fit the data.
		this.setVisible(true);
	}
	
	public static void main(String[] args) {
		/*
		LineChart<String> chart = new LineChart<String>(
		         "Window title" ,
		         null,
		         "xlabel",
		         "ylabel",
		         new String[] {"unu", "doi", "trei", "patru", "cinci", "sase", "sapte", "opt", "noua"},
		         new Integer[] {1, 4, 9, 16, 25, 36, 49, 64, 81});
		*/
		LineChart<String> chart = new LineChart<String>(
				new String[] {"unu", "doi", "trei", "patru", "cinci", "sase", "sapte", "opt", "noua"},
		        new Integer[] {1, 4, 9, 16, 25, 36, 49, 64, 81}
		);
		chart.display();
	}
}
