"""Data-related tools for the PrismIQ agent.

These tools provide access to segmentation, EDA summary, and external context data.
"""

from __future__ import annotations

from langchain_core.tools import Tool
from loguru import logger

from src.agent.utils import sanitize_error_message


def _format_segment_description(segment_name: str) -> str:
    """Format a segment name into a human-readable description.

    Args:
        segment_name: The segment name (e.g., "Urban_Evening_Premium").

    Returns:
        Human-readable description of the segment.

    Note:
        This assumes segment names follow the pattern:
        "{Location}_{TimeProfile}_{VehicleType}" (e.g., "Urban_Evening_Premium")

        If the format doesn't match, returns a generic description.
        If segment naming conventions change, update this logic.
    """
    try:
        parts = segment_name.split("_")
        if len(parts) >= 3:
            location, time_profile, vehicle = parts[0], parts[1], parts[2]
            return (
                f"{location} area during {time_profile.lower()} hours "
                f"with {vehicle.lower()} vehicle preference"
            )
        elif len(parts) == 2:
            # Handle 2-part names gracefully
            return f"{parts[0]} {parts[1].lower()} segment"
        else:
            return f"Market segment: {segment_name}"
    except (AttributeError, IndexError) as e:
        logger.warning(f"Unexpected segment name format '{segment_name}': {e}")
        return f"Market segment: {segment_name}"


def create_get_segment_tool() -> Tool:
    """Create the get_segment tool for market segmentation.

    Returns:
        LangChain Tool that classifies market context into segments.
    """

    def get_segment(_input: str) -> str:
        """Classify the current market context into a segment."""
        from src.agent.context import get_current_context
        from src.ml.segmenter import Segmenter

        try:
            context = get_current_context()
            segmenter = Segmenter.load()

            result = segmenter.classify(context)

            # Generate human-readable description from segment name
            # Note: This parsing assumes segment names follow the pattern:
            # "{Location}_{TimeProfile}_{VehicleType}" (e.g., "Urban_Evening_Premium")
            # If segment naming conventions change, update this logic.
            description = _format_segment_description(result.segment_name)

            # Determine confidence level
            if result.centroid_distance < 1.0:
                confidence = "high"
            elif result.centroid_distance < 2.0:
                confidence = "medium"
            else:
                confidence = "low"

            characteristics_text = "\n".join([
                f"  - {k}: {v:.2f}" if isinstance(v, float) else f"  - {k}: {v}"
                for k, v in result.characteristics.items()
            ])

            return (
                f"Segment: {result.segment_name}\n"
                f"Description: {description}\n"
                f"Cluster ID: {result.cluster_id}\n"
                f"Confidence Level: {confidence}\n"
                f"Centroid Distance: {result.centroid_distance:.3f}\n\n"
                f"Segment Characteristics:\n{characteristics_text}"
            )

        except FileNotFoundError:
            return "Error: Segmentation model not available. Please train the model first."
        except Exception as e:
            logger.error(f"get_segment tool error: {e}")
            return f"Error classifying segment: {sanitize_error_message(e)}"

    return Tool(
        name="get_segment",
        description=(
            "Classify the current market context into a customer segment. "
            "Use this when the user asks about segments, customer classification, "
            "market categories, or which group a context belongs to. "
            "Returns segment name, description, and characteristics."
        ),
        func=get_segment,
    )


def create_get_eda_summary_tool() -> Tool:
    """Create the get_eda_summary tool for dataset statistics.

    Returns:
        LangChain Tool that returns dataset summary and statistics.
    """

    def get_eda_summary(_input: str) -> str:
        """Get summary statistics of the pricing dataset."""
        from src.ml.preprocessor import load_dataset

        try:
            df = load_dataset()

            # Calculate statistics
            row_count = len(df)
            col_count = len(df.columns)
            segments = sorted(df["Customer_Loyalty_Status"].unique().tolist())

            price_min = df["Historical_Cost_of_Ride"].min()
            price_max = df["Historical_Cost_of_Ride"].max()
            price_mean = df["Historical_Cost_of_Ride"].mean()
            price_std = df["Historical_Cost_of_Ride"].std()

            # Additional statistics
            avg_riders = df["Number_of_Riders"].mean()
            avg_drivers = df["Number_of_Drivers"].mean()
            avg_duration = df["Expected_Ride_Duration"].mean()
            avg_rating = df["Average_Ratings"].mean()

            location_dist = df["Location_Category"].value_counts().to_dict()
            vehicle_dist = df["Vehicle_Type"].value_counts().to_dict()

            return (
                f"Dataset Summary:\n"
                f"  - Total Records: {row_count:,}\n"
                f"  - Total Features: {col_count}\n"
                f"  - Customer Segments: {', '.join(segments)}\n\n"
                f"Price Statistics:\n"
                f"  - Range: ${price_min:.2f} - ${price_max:.2f}\n"
                f"  - Mean: ${price_mean:.2f}\n"
                f"  - Std Dev: ${price_std:.2f}\n\n"
                f"Demand/Supply Averages:\n"
                f"  - Avg Riders: {avg_riders:.1f}\n"
                f"  - Avg Drivers: {avg_drivers:.1f}\n"
                f"  - Avg Duration: {avg_duration:.1f} min\n"
                f"  - Avg Rating: {avg_rating:.2f}\n\n"
                f"Location Distribution: {location_dist}\n"
                f"Vehicle Distribution: {vehicle_dist}"
            )

        except FileNotFoundError:
            return "Error: Dataset not found. Please ensure the data file exists."
        except Exception as e:
            logger.error(f"get_eda_summary tool error: {e}")
            return f"Error loading dataset summary: {sanitize_error_message(e)}"

    return Tool(
        name="get_eda_summary",
        description=(
            "Get summary statistics and overview of the pricing dataset. "
            "Use this when the user asks about the data, dataset statistics, "
            "exploratory analysis, or wants to understand the training data. "
            "Returns row counts, price ranges, and distribution statistics."
        ),
        func=get_eda_summary,
    )


def create_get_external_context_tool() -> Tool:
    """Create the get_external_context tool for external factors.

    Returns:
        LangChain Tool that returns current external context (weather, events, etc.).

    Warning:
        This tool currently returns SIMULATED DATA for demonstration purposes.
        In production, integrate with real external APIs via n8n workflows:
        - Weather: OpenWeatherMap, Weather.com API
        - Events: Ticketmaster, Eventbrite APIs
        - Fuel: GasBuddy, EIA APIs

    TODO:
        - Add mode flag (simulated/production) to toggle data source
        - Implement n8n webhook integration for real-time data
        - Add caching layer for external API responses
    """

    def get_external_context(_input: str) -> str:
        """Get current external factors affecting pricing.

        WARNING: Returns SIMULATED data for demonstration purposes only.
        """
        # ⚠️ SIMULATED DATA - NOT REAL-TIME
        # In production, this would fetch from external APIs via n8n workflows.
        # See tool docstring for integration plan.

        return (
            "⚠️ SIMULATED DATA - FOR DEMONSTRATION ONLY ⚠️\n"
            "=" * 45 + "\n\n"
            "External Context:\n\n"
            "Weather:\n"
            "  - Condition: Partly Cloudy\n"
            "  - Temperature: 72°F (22°C)\n"
            "  - Precipitation: 10% chance\n"
            "  - Impact: Neutral - normal demand expected\n\n"
            "Events:\n"
            "  - No major events in the area\n"
            "  - Normal traffic conditions\n\n"
            "Fuel Prices:\n"
            "  - Regular: $3.45/gallon\n"
            "  - Premium: $4.15/gallon\n"
            "  - Trend: Stable (no significant change)\n\n"
            "─" * 45 + "\n"
            "Note: In production, this data would be fetched from external APIs "
            "(weather services, event databases, fuel price feeds) via n8n workflows."
        )

    return Tool(
        name="get_external_context",
        description=(
            "Get current external factors that might affect pricing, including weather, "
            "events, and fuel prices. Use this when the user asks about external factors, "
            "weather impact, events in the area, or fuel prices. "
            "⚠️ IMPORTANT: Currently returns SIMULATED data for demonstration only."
        ),
        func=get_external_context,
    )

