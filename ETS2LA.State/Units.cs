using static ETS2LA.Translations.T;

namespace ETS2LA.State;

public enum UnitType
{
    Speed,
    Distance,
    Liquid,
    Weight,
    Temperature,
    Pressure
}

public enum Units
{
    Metric,
    Imperial,
    Scientific
}

public static class UnitConversions
{
    public static float ToScientificUnits(UnitType type, float value, Units fromUnits)
    {
        switch (type)
        {
            case UnitType.Speed:
                switch (fromUnits)
                {
                    case Units.Metric:
                        return value / 3.6f; // km/h to m/s
                    case Units.Imperial:
                        return value * 0.44704f; // mph to m/s
                    case Units.Scientific:
                        return value; // already in m/s
                }
                break;
            case UnitType.Distance:
                switch (fromUnits)
                {
                    case Units.Metric:
                        return value; // already in m
                    case Units.Imperial:
                        return value * 0.3048f; // ft to m
                    case Units.Scientific:
                        return value; // already in m
                }
                break;
            case UnitType.Liquid:
                switch (fromUnits)
                {
                    case Units.Metric:
                        return value; // already in liters
                    case Units.Imperial:
                        return value * 4.54609f; // gallons to liters
                    case Units.Scientific:
                        return value; // already in liters
                }
                break;
            case UnitType.Weight:
                switch (fromUnits)       
                {
                    case Units.Metric:
                        return value; // already in kg
                    case Units.Imperial:
                        return value * 0.453592f; // lbs to kg
                    case Units.Scientific:
                        return value; // already in kg
                }
                break;
            case UnitType.Temperature:
                switch (fromUnits)
                {
                    case Units.Metric:
                        return value + 273.15f; // Celsius to Kelvin
                    case Units.Imperial:
                        return (value - 32) * 5 / 9 + 273.15f; // Fahrenheit to Kelvin
                    case Units.Scientific:
                        return value; // already in Kelvin
                }
                break;
            case UnitType.Pressure:
                switch (fromUnits)
                {                    
                    case Units.Metric:
                        return value * 100f; // bar to Pa
                    case Units.Imperial:
                        return value * 6894.76f; // psi to Pa
                    case Units.Scientific:
                        return value; // already in Pa
                }
                break;
        }
        throw new NotImplementedException($"Conversion for {type} from {fromUnits} is not implemented.");
    }

    public static float FromScientificUnits(UnitType type, float value, Units toUnits)
    {
        switch (type)
        {
            case UnitType.Speed:
                switch (toUnits)
                {
                    case Units.Metric:
                        return value * 3.6f; // m/s to km/h
                    case Units.Imperial:
                        return value / 0.44704f; // m/s to mph
                    case Units.Scientific:
                        return value; // already in m/s
                }
                break;
            case UnitType.Distance:
                switch (toUnits)
                {
                    case Units.Metric:
                        return value; // already in m
                    case Units.Imperial:
                        return value / 0.3048f; // m to ft
                    case Units.Scientific:
                        return value; // already in m
                }
                break;
            case UnitType.Liquid:
                switch (toUnits)
                {
                    case Units.Metric:
                        return value; // already in liters
                    case Units.Imperial:
                        return value / 4.54609f; // liters to gallons
                    case Units.Scientific:
                        return value; // already in liters
                }
                break;
            case UnitType.Weight:
                switch (toUnits)       
                {
                    case Units.Metric:
                        return value; // already in kg
                    case Units.Imperial:
                        return value / 0.453592f; // kg to lbs
                    case Units.Scientific:
                        return value; // already in kg
                }
                break;
            case UnitType.Temperature:
                switch (toUnits)
                {
                    case Units.Metric:
                        return value - 273.15f; // Kelvin to Celsius
                    case Units.Imperial:
                        return (value - 273.15f) * 9 / 5 + 32; // Kelvin to Fahrenheit
                    case Units.Scientific:
                        return value; // already in Kelvin
                }
                break;
            case UnitType.Pressure:
                switch (toUnits)
                {                    
                    case Units.Metric:
                        return value / 100f; // Pa to bar
                    case Units.Imperial:
                        return value / 6894.76f; // Pa to psi
                    case Units.Scientific:
                        return value; // already in Pa
                }
                break;
        }
        throw new NotImplementedException($"Conversion for {type} to {toUnits} is not implemented.");
    }

    public static string GetUnitName(UnitType type, Units units)
    {
        switch (type)
        {
            case UnitType.Speed:
                switch (units)
                {
                    case Units.Metric:
                        return _("kilometers per hour");
                    case Units.Imperial:
                        return _("miles per hour");
                    case Units.Scientific:
                        return _("meters per second");
                }
                break;
            case UnitType.Distance:
                switch (units)
                {
                    case Units.Metric:
                        return _("meters");
                    case Units.Imperial:
                        return _("feet");
                    case Units.Scientific:
                        return _("meters");
                }
                break;
            case UnitType.Liquid:
                switch (units)
                {
                    case Units.Metric:
                        return _("liters");
                    case Units.Imperial:
                        return _("gallons");
                    case Units.Scientific:
                        return _("liters");
                }
                break;
            case UnitType.Weight:
                switch (units)       
                {
                    case Units.Metric:
                        return _("kilograms");
                    case Units.Imperial:
                        return _("pounds");
                    case Units.Scientific:
                        return _("kilograms");
                }
                break;
            case UnitType.Temperature:
                switch (units)
                {
                    case Units.Metric:
                        return _("°C");
                    case Units.Imperial:
                        return _("°F");
                    case Units.Scientific:
                        return _("K");
                }
                break;
            case UnitType.Pressure:
                switch (units)
                {                    
                    case Units.Metric:
                        return _("bar");
                    case Units.Imperial:
                        return _("psi");
                    case Units.Scientific:
                        return _("Pascals");
                }
                break;
        }
        throw new NotImplementedException($"Unit name for {type} in {units} is not implemented.");
    }

    public static string GetUnitAbbreviation(UnitType type, Units units)
    {
        switch (type)
        {
            case UnitType.Speed:
                switch (units)
                {
                    case Units.Metric:
                        return _("km/h");
                    case Units.Imperial:
                        return _("mph");
                    case Units.Scientific:
                        return _("m/s");
                }
                break;
            case UnitType.Distance:
                switch (units)
                {
                    case Units.Metric:
                        return _("m");
                    case Units.Imperial:
                        return _("ft");
                    case Units.Scientific:
                        return _("m");
                }
                break;
            case UnitType.Liquid:
                switch (units)
                {
                    case Units.Metric:
                        return _("L");
                    case Units.Imperial:
                        return _("gal");
                    case Units.Scientific:
                        return _("L");
                }
                break;
            case UnitType.Weight:
                switch (units)       
                {
                    case Units.Metric:
                        return _("kg");
                    case Units.Imperial:
                        return _("lbs");
                    case Units.Scientific:
                        return _("kg");
                }
                break;
            case UnitType.Temperature:
                switch (units)
                {
                    case Units.Metric:
                        return _("°C");
                    case Units.Imperial:
                        return _("°F");
                    case Units.Scientific:
                        return _("K");
                }
                break;
            case UnitType.Pressure:
                switch (units)
                {                    
                    case Units.Metric:
                        return _("bar");
                    case Units.Imperial:
                        return _("psi");
                    case Units.Scientific:
                        return _("Pa");
                }
                break;
        }
        throw new NotImplementedException($"Unit abbreviation for {type} in {units} is not implemented.");
    }
}