"use client";

import { useEffect, useRef, useCallback } from "react";
import {
  createChart,
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  ColorType,
  CrosshairMode,
  type IChartApi,
  type ISeriesApi,
  type CandlestickData,
  type HistogramData,
  type LineData,
  type Time,
} from "lightweight-charts";
import { useTheme } from "next-themes";

interface OHLCVData {
  timestamp: number; // Unix seconds
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

interface CandlestickChartProps {
  data: OHLCVData[];
  indicators?: {
    ema20?: boolean;
    ema50?: boolean;
    sma50?: boolean;
    sma200?: boolean;
    bollinger?: boolean;
    volume?: boolean;
    rsi?: boolean;
    macd?: boolean;
  };
  height?: number;
  className?: string;
}

// Simple EMA calculation
function calculateEMA(data: OHLCVData[], period: number): LineData[] {
  const emaData: LineData[] = [];
  if (data.length < period) return emaData;
  const k = 2 / (period + 1);
  let ema = data.slice(0, period).reduce((sum, d) => sum + d.close, 0) / period;
  for (let i = period; i < data.length; i++) {
    ema = data[i].close * k + ema * (1 - k);
    emaData.push({ time: data[i].timestamp as Time, value: ema });
  }
  return emaData;
}

// Simple SMA calculation
function calculateSMA(data: OHLCVData[], period: number): LineData[] {
  const smaData: LineData[] = [];
  for (let i = period - 1; i < data.length; i++) {
    const sum = data.slice(i - period + 1, i + 1).reduce((s, d) => s + d.close, 0);
    smaData.push({ time: data[i].timestamp as Time, value: sum / period });
  }
  return smaData;
}

// Bollinger Bands
function calculateBollinger(
  data: OHLCVData[],
  period: number = 20,
  stdDev: number = 2
) {
  const upper: LineData[] = [];
  const middle: LineData[] = [];
  const lower: LineData[] = [];

  for (let i = period - 1; i < data.length; i++) {
    const slice = data.slice(i - period + 1, i + 1);
    const sma = slice.reduce((s, d) => s + d.close, 0) / period;
    const variance = slice.reduce((s, d) => s + Math.pow(d.close - sma, 2), 0) / period;
    const std = Math.sqrt(variance);
    const time = data[i].timestamp as Time;
    upper.push({ time, value: sma + stdDev * std });
    middle.push({ time, value: sma });
    lower.push({ time, value: sma - stdDev * std });
  }
  return { upper, middle, lower };
}

export function CandlestickChart({
  data,
  indicators = { volume: true },
  height = 500,
  className,
}: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const { theme } = useTheme();
  const isDark = theme === "dark";

  const initChart = useCallback(() => {
    if (!containerRef.current || data.length === 0) return;

    if (chartRef.current) {
      chartRef.current.remove();
      chartRef.current = null;
    }

    const container = containerRef.current;
    const colors = isDark
      ? {
          bg: "#0F172A",
          text: "#94A3B8",
          border: "#1E293B",
          candleUp: "#22C55E",
          candleDown: "#EF4444",
          wick: "#64748B",
        }
      : {
          bg: "#FFFFFF",
          text: "#64748B",
          border: "#E2E8F0",
          candleUp: "#22C55E",
          candleDown: "#EF4444",
          wick: "#94A3B8",
        };

    const chart = createChart(container, {
      layout: {
        background: { type: ColorType.Solid, color: colors.bg },
        textColor: colors.text,
      },
      grid: {
        vertLines: { color: colors.border },
        horzLines: { color: colors.border },
      },
      crosshair: { mode: CrosshairMode.Normal },
      rightPriceScale: { borderColor: colors.border },
      timeScale: {
        borderColor: colors.border,
        timeVisible: true,
        secondsVisible: false,
        tickMarkFormatter: (time: number) => {
          const d = new Date(time * 1000);
          const mm = String(d.getMonth() + 1).padStart(2, "0");
          const dd = String(d.getDate()).padStart(2, "0");
          const hh = String(d.getHours()).padStart(2, "0");
          const min = String(d.getMinutes()).padStart(2, "0");
          // Show date+time for intraday, just date for daily
          return `${mm}/${dd} ${hh}:${min}`;
        },
      },
      width: container.clientWidth,
      height,
    });

    chartRef.current = chart;

    // Candlestick series (v5 API)
    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: colors.candleUp,
      downColor: colors.candleDown,
      borderUpColor: colors.candleUp,
      borderDownColor: colors.candleDown,
      wickUpColor: colors.wick,
      wickDownColor: colors.wick,
    });

    const candleData: CandlestickData[] = data.map((d) => ({
      time: d.timestamp as Time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }));
    candleSeries.setData(candleData);

    // Volume
    if (indicators.volume !== false) {
      const volumeSeries = chart.addSeries(HistogramSeries, {
        priceFormat: { type: "volume" },
        priceScaleId: "volume",
      });
      volumeSeries.priceScale().applyOptions({
        scaleMargins: { top: 0.85, bottom: 0 },
      });
      const volumeData: HistogramData[] = data.map((d) => ({
        time: d.timestamp as Time,
        value: d.volume,
        color: d.close >= d.open ? `${colors.candleUp}40` : `${colors.candleDown}40`,
      }));
      volumeSeries.setData(volumeData);
    }

    // EMA 20
    if (indicators.ema20) {
      const ema20 = calculateEMA(data, 20);
      const series = chart.addSeries(LineSeries, { color: "#F59E0B", lineWidth: 2 });
      series.setData(ema20);
    }

    // EMA 50
    if (indicators.ema50) {
      const ema50 = calculateEMA(data, 50);
      const series = chart.addSeries(LineSeries, { color: "#8B5CF6", lineWidth: 2 });
      series.setData(ema50);
    }

    // SMA 50
    if (indicators.sma50) {
      const sma50 = calculateSMA(data, 50);
      const series = chart.addSeries(LineSeries, { color: "#06B6D4", lineWidth: 1, lineStyle: 2 });
      series.setData(sma50);
    }

    // SMA 200
    if (indicators.sma200) {
      const sma200 = calculateSMA(data, 200);
      const series = chart.addSeries(LineSeries, { color: "#EC4899", lineWidth: 1, lineStyle: 2 });
      series.setData(sma200);
    }

    // Bollinger Bands
    if (indicators.bollinger) {
      const { upper, middle, lower } = calculateBollinger(data);
      chart.addSeries(LineSeries, { color: "#6366F1", lineWidth: 1, lineStyle: 2 }).setData(upper);
      chart.addSeries(LineSeries, { color: "#6366F1", lineWidth: 1 }).setData(middle);
      chart.addSeries(LineSeries, { color: "#6366F1", lineWidth: 1, lineStyle: 2 }).setData(lower);
    }

    chart.timeScale().fitContent();
    return chart;
  }, [data, isDark, height, indicators]);

  useEffect(() => {
    const chart = initChart();
    const handleResize = () => {
      if (containerRef.current && chartRef.current) {
        chartRef.current.applyOptions({ width: containerRef.current.clientWidth });
      }
    };
    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
      if (chartRef.current) {
        chartRef.current.remove();
        chartRef.current = null;
      }
    };
  }, [initChart]);

  return (
    <div ref={containerRef} className={className} style={{ width: "100%", minHeight: height }} />
  );
}
