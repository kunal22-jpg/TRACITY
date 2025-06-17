import React, { useMemo } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
} from 'chart.js';
import { Line, Bar, Pie, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
  Filler
);

const ChartComponent = ({ data, chartType = 'bar', height = 300, showYearSeparately = false }) => {
  const chartData = useMemo(() => {
    if (!data || data.length === 0) return null;

    // Extract keys from first data item (excluding common non-numeric fields)
    const firstItem = data[0];
    const excludeKeys = ['_id', 'id', 'name', 'title', 'description', 'category', 'type', 'date'];
    
    const numericKeys = Object.keys(firstItem).filter(key => {
      const value = firstItem[key];
      return typeof value === 'number' && !excludeKeys.includes(key);
    });

    const stringKeys = Object.keys(firstItem).filter(key => {
      const value = firstItem[key];
      return typeof value === 'string' && !excludeKeys.includes(key);
    });

    // Prioritize 'state' as label if available, otherwise use first string field
    let labelKey = 'state';
    if (!stringKeys.includes('state')) {
      labelKey = stringKeys[0] || Object.keys(firstItem)[0];
    }

    // Choose the most relevant numeric field based on dataset
    let dataKey = numericKeys[0];
    
    // Smart field selection based on available fields
    if (numericKeys.includes('cases_reported')) {
      dataKey = 'cases_reported';
    } else if (numericKeys.includes('literacy_rate')) {
      dataKey = 'literacy_rate';
    } else if (numericKeys.includes('avg_aqi')) {
      dataKey = 'avg_aqi';
    } else if (numericKeys.includes('power_consumption_gwh')) {
      dataKey = 'power_consumption_gwh';
    } else if (numericKeys.includes('deaths')) {
      dataKey = 'deaths';
    }

    if (!dataKey) return null;

    // Check if we have year data for year-wise separation
    const hasYearData = data.some(item => item.year);
    
    if (showYearSeparately && hasYearData) {
      // Group data by year, then by state
      const yearGroups = {};
      data.forEach(item => {
        const year = item.year || 'Unknown';
        const label = item[labelKey]?.toString() || `Item ${data.indexOf(item) + 1}`;
        const value = typeof item[dataKey] === 'number' ? item[dataKey] : 0;
        
        if (!yearGroups[year]) {
          yearGroups[year] = {};
        }
        if (!yearGroups[year][label]) {
          yearGroups[year][label] = [];
        }
        yearGroups[year][label].push(value);
      });

      // Create datasets for each year
      const years = Object.keys(yearGroups).sort();
      const allStates = [...new Set(data.map(item => item[labelKey]?.toString()).filter(Boolean))].sort();
      
      // Enhanced vibrant color palette for year-wise data
      const yearColors = [
        { bg: 'rgba(99, 102, 241, 0.8)', border: 'rgb(99, 102, 241)' },     // Indigo
        { bg: 'rgba(59, 130, 246, 0.8)', border: 'rgb(59, 130, 246)' },     // Blue  
        { bg: 'rgba(16, 185, 129, 0.8)', border: 'rgb(16, 185, 129)' },     // Emerald
        { bg: 'rgba(245, 158, 11, 0.8)', border: 'rgb(245, 158, 11)' },     // Amber
        { bg: 'rgba(239, 68, 68, 0.8)', border: 'rgb(239, 68, 68)' },       // Red
        { bg: 'rgba(139, 92, 246, 0.8)', border: 'rgb(139, 92, 246)' },     // Violet
        { bg: 'rgba(236, 72, 153, 0.8)', border: 'rgb(236, 72, 153)' },     // Pink
        { bg: 'rgba(20, 184, 166, 0.8)', border: 'rgb(20, 184, 166)' },     // Teal
        { bg: 'rgba(251, 146, 60, 0.8)', border: 'rgb(251, 146, 60)' },     // Orange
        { bg: 'rgba(34, 197, 94, 0.8)', border: 'rgb(34, 197, 94)' },       // Green
      ];

      const datasets = years.map((year, yearIndex) => {
        const yearData = allStates.map(state => {
          const stateValues = yearGroups[year][state] || [0];
          return stateValues.reduce((sum, val) => sum + val, 0) / stateValues.length;
        });

        const color = yearColors[yearIndex % yearColors.length];
        
        return {
          label: `${year} - ${dataKey.replace('_', ' ').toUpperCase()}`,
          data: yearData,
          backgroundColor: chartType === 'line' ? color.bg.replace('0.8', '0.2') : color.bg,
          borderColor: color.border,
          borderWidth: 2,
          fill: chartType === 'line',
          tension: chartType === 'line' ? 0.4 : undefined,
        };
      });

      return {
        labels: allStates,
        datasets: datasets
      };
    } else {
      // Original logic for non-year-separated data
      const groupedData = {};
      data.forEach(item => {
        const label = item[labelKey]?.toString() || `Item ${data.indexOf(item) + 1}`;
        const value = typeof item[dataKey] === 'number' ? item[dataKey] : 0;
        
        if (!groupedData[label]) {
          groupedData[label] = [];
        }
        groupedData[label].push(value);
      });

      const labels = Object.keys(groupedData);
      const values = labels.map(label => {
        const values = groupedData[label];
        return values.length > 1 ? 
          values.reduce((sum, val) => sum + val, 0) / values.length :
          values[0];
      });

      // Sort by values for better visualization (descending order)
      const sortedIndices = values
        .map((value, index) => ({ value, index }))
        .sort((a, b) => b.value - a.value)
        .map(item => item.index);

      const sortedLabels = sortedIndices.map(i => labels[i]);
      const sortedValues = sortedIndices.map(i => values[i]);

      // Dynamic limit based on chart type and container
      const maxItems = chartType === 'pie' || chartType === 'doughnut' ? 10 : sortedLabels.length;
      const finalLabels = sortedLabels.slice(0, maxItems);
      const finalValues = sortedValues.slice(0, maxItems);

      // Enhanced vibrant color palette that works in both day and night modes
      const enhancedColors = [
        'rgba(99, 102, 241, 0.85)',   // Bright Indigo
        'rgba(59, 130, 246, 0.85)',   // Bright Blue
        'rgba(16, 185, 129, 0.85)',   // Bright Emerald
        'rgba(245, 158, 11, 0.85)',   // Bright Amber
        'rgba(239, 68, 68, 0.85)',    // Bright Red
        'rgba(139, 92, 246, 0.85)',   // Bright Violet
        'rgba(236, 72, 153, 0.85)',   // Bright Pink
        'rgba(20, 184, 166, 0.85)',   // Bright Teal
        'rgba(251, 146, 60, 0.85)',   // Bright Orange
        'rgba(34, 197, 94, 0.85)',    // Bright Green
        'rgba(168, 85, 247, 0.85)',   // Bright Purple
        'rgba(14, 165, 233, 0.85)',   // Bright Sky Blue
        'rgba(217, 70, 239, 0.85)',   // Bright Fuchsia
        'rgba(34, 211, 238, 0.85)',   // Bright Cyan
        'rgba(244, 63, 94, 0.85)',    // Bright Rose
        'rgba(52, 211, 153, 0.85)',   // Bright Emerald Alt
        'rgba(251, 191, 36, 0.85)',   // Bright Yellow
        'rgba(124, 58, 237, 0.85)',   // Bright Purple Alt
        'rgba(248, 113, 113, 0.85)',  // Bright Red Alt
        'rgba(96, 165, 250, 0.85)',   // Bright Blue Alt
      ];

      const enhancedBorderColors = enhancedColors.map(color => color.replace('0.85', '1'));

      if (chartType === 'pie' || chartType === 'doughnut') {
        return {
          labels: finalLabels,
          datasets: [{
            label: dataKey.replace('_', ' ').toUpperCase(),
            data: finalValues,
            backgroundColor: enhancedColors.slice(0, finalLabels.length),
            borderColor: enhancedBorderColors.slice(0, finalLabels.length),
            borderWidth: 2,
          }]
        };
      }

      return {
        labels: finalLabels,
        datasets: [{
          label: dataKey.replace('_', ' ').toUpperCase(),
          data: finalValues,
          backgroundColor: chartType === 'line' ? 'rgba(99, 102, 241, 0.2)' : enhancedColors.slice(0, finalLabels.length),
          borderColor: chartType === 'line' ? enhancedBorderColors[0] : enhancedBorderColors.slice(0, finalLabels.length),
          borderWidth: 2,
          fill: chartType === 'line',
          tension: chartType === 'line' ? 0.4 : undefined,
        }]
      };
    }
  }, [data, chartType, showYearSeparately]);

  const options = useMemo(() => {
    // Check if we need horizontal scrolling (many states/labels)
    const labelCount = chartData?.labels?.length || 0;
    const needsScroll = labelCount > 15 && (chartType === 'bar');

    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: chartType === 'pie' || chartType === 'doughnut' ? 'right' : 'top',
          labels: {
            color: '#F1F5F9',
            font: {
              size: 12,
              weight: '500'
            },
            padding: 15,
            usePointStyle: true,
            boxWidth: 12,
            generateLabels: (chart) => {
              const original = ChartJS.defaults.plugins.legend.labels.generateLabels;
              const labels = original.call(this, chart);
              
              // Enhanced legend styling for better visibility
              labels.forEach(label => {
                label.fillStyle = label.fillStyle;
                label.strokeStyle = label.strokeStyle;
                label.lineWidth = 2;
              });
              
              return labels;
            }
          },
          // Make legend scrollable for pie charts with many items
          ...(chartType === 'pie' || chartType === 'doughnut' ? {
            maxHeight: 200,
            position: 'right'
          } : {})
        },
        tooltip: {
          backgroundColor: 'rgba(30, 41, 59, 0.95)',
          titleColor: '#F1F5F9',
          bodyColor: '#F1F5F9',
          borderColor: 'rgba(99, 102, 241, 0.6)',
          borderWidth: 2,
          cornerRadius: 8,
          titleFont: {
            size: 14,
            weight: 'bold'
          },
          bodyFont: {
            size: 13
          },
          padding: 12,
          displayColors: true,
          intersect: false,
          mode: 'index'
        }
      },
      // Enhanced scales with horizontal scrolling support
      scales: chartType !== 'pie' && chartType !== 'doughnut' ? {
        x: {
          ticks: {
            color: '#94A3B8',
            font: {
              size: needsScroll ? 9 : 11,
              weight: '500'
            },
            maxRotation: needsScroll ? 90 : 45,
            minRotation: needsScroll ? 45 : 0,
          },
          grid: {
            color: 'rgba(148, 163, 184, 0.15)',
            lineWidth: 1
          },
          border: {
            color: 'rgba(148, 163, 184, 0.3)',
            width: 1
          }
        },
        y: {
          ticks: {
            color: '#94A3B8',
            font: {
              size: 11,
              weight: '500'
            },
            callback: function(value) {
              // Format large numbers with K, M suffixes
              if (value >= 1000000) {
                return (value / 1000000).toFixed(1) + 'M';
              } else if (value >= 1000) {
                return (value / 1000).toFixed(1) + 'K';
              }
              return value;
            }
          },
          grid: {
            color: 'rgba(148, 163, 184, 0.15)',
            lineWidth: 1
          },
          border: {
            color: 'rgba(148, 163, 184, 0.3)',
            width: 1
          }
        }
      } : undefined,
      // Enhanced interaction options
      interaction: {
        intersect: false,
        mode: 'index'
      },
      elements: {
        bar: {
          borderRadius: 4,
          borderSkipped: false,
        },
        point: {
          radius: 4,
          hoverRadius: 6,
          borderWidth: 2,
          hoverBorderWidth: 3
        },
        line: {
          borderWidth: 3,
          borderCapStyle: 'round'
        }
      },
      // Animation settings
      animation: {
        duration: 1000,
        easing: 'easeInOutQuart'
      },
      hover: {
        animationDuration: 200
      }
    };
  }, [chartType, chartData]);

  if (!chartData) {
    return (
      <div className="flex items-center justify-center h-48 text-slate-400">
        <div className="text-center">
          <div className="text-2xl mb-2">📊</div>
          <div className="text-sm">No data available for visualization</div>
        </div>
      </div>
    );
  }

  const renderChart = () => {
    const labelCount = chartData?.labels?.length || 0;
    const needsHorizontalScroll = labelCount > 15 && (chartType === 'bar');
    
    // Calculate dynamic width for horizontal scrolling
    const minBarWidth = 40; // Minimum width per bar
    const dynamicWidth = needsHorizontalScroll ? Math.max(800, labelCount * minBarWidth) : '100%';
    
    const chartProps = {
      data: chartData,
      options: options
    };

    const chartElement = (() => {
      switch (chartType) {
        case 'line':
          return <Line {...chartProps} />;
        case 'pie':
          return <Pie {...chartProps} />;
        case 'doughnut':
          return <Doughnut {...chartProps} />;
        case 'bar':
        default:
          return <Bar {...chartProps} />;
      }
    })();

    // Wrap in scrollable container if needed
    if (needsHorizontalScroll) {
      return (
        <div className="overflow-x-auto overflow-y-hidden">
          <div style={{ width: dynamicWidth, minWidth: '800px' }}>
            {chartElement}
          </div>
        </div>
      );
    }

    // For pie charts with many items, add scrollable legend
    if ((chartType === 'pie' || chartType === 'doughnut') && labelCount > 8) {
      return (
        <div className="flex h-full">
          <div className="flex-1 pr-4">
            {chartElement}
          </div>
        </div>
      );
    }

    return chartElement;
  };

  return (
    <div className="w-full" style={{ height: `${height}px` }}>
      {renderChart()}
    </div>
  );
};

export default ChartComponent;
