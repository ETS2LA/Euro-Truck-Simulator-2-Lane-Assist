using System.Collections.Generic;
using System.Drawing;

namespace ETS2LA.Game.Extractor
{
    public abstract class TsPrefabLook
    {
        public int ZIndex { get; set; }
        public Brush Color { get; set; }
        protected readonly List<PointF> Points;

        protected TsPrefabLook(List<PointF> points)
        {
            Points = points;
        }

        protected TsPrefabLook() : this(new List<PointF>()) { }

        public void AddPoint(PointF p)
        {
            Points.Add(p);
        }

        public void AddPoint(float x, float y)
        {
            AddPoint(new PointF(x, y));
        }
    }

    public class TsPrefabRoadLook : TsPrefabLook
    {
        public float Width { private get; set; }

        public TsPrefabRoadLook()
        {
            ZIndex = 1;
        }

    }

    public class TsPrefabPolyLook : TsPrefabLook
    {
        public TsPrefabPolyLook(List<PointF> points) : base(points) { }
    }
}