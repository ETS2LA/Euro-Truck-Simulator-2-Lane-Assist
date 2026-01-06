using System.Numerics;
using ETS2LA.Game.Extractor.Helpers;

namespace ETS2LA.Game.Extractor
{
    public class TsNode
    {
        public ulong Uid { get; }

        public float X { get; }
        public float Y { get; }
        public float Z { get; }

        /// <summary>
        /// This node's rotation as a quaternion, in the order (X, Y, Z, W).
        /// </summary>
        public Vector4 Quaternion { get; }

        /// <summary>
        /// This node's rotation in radians around the Y-axis (up vector, yaw).
        /// </summary>
        public float Rotation { get; }

        public TsNode(TsSector sector, int fileOffset)
        {
            Uid = MemoryHelper.ReadUInt64(sector.Stream, fileOffset);
            X = MemoryHelper.ReadInt32(sector.Stream, fileOffset += 0x08) / 256f;
            Z = MemoryHelper.ReadInt32(sector.Stream, fileOffset += 0x08) / 256f;
            Y = MemoryHelper.ReadInt32(sector.Stream, fileOffset += 0x08) / 256f;

            var qW = MemoryHelper.ReadSingle(sector.Stream, fileOffset += 0x04);
            var qX = MemoryHelper.ReadSingle(sector.Stream, fileOffset += 0x04);
            var qY = MemoryHelper.ReadSingle(sector.Stream, fileOffset += 0x04);
            var qZ = MemoryHelper.ReadSingle(sector.Stream, fileOffset += 0x04);

            var rot = Math.PI - Math.Atan2(qY, qW);
            Rotation = (float) (rot % Math.PI * 2);

            Quaternion = new Vector4(qX, qY, qZ, qW);

            // TODO: Parse navigation data from flags, example: 
            // https://github.com/truckermudgeon/maps/blob/main/packages/clis/parser/game-files/sector-parser.ts#L886
        }
    }
}