// adapted from https://github.com/Siccity/GLTFUtility/blob/master/Scripts/BufferedBinaryReader.cs
using System;
using System.IO;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;

namespace Simulate.GLTF {
    public class BufferedBinaryReader : IDisposable {
        readonly Stream stream;
        readonly byte[] buffer;
        readonly int bufferSize;

        int bufferOffset;
        int bufferedBytes;
        int byteStride;

        Bit2Converter bit2Converter;
        Bit4Converter bit4Converter;

        public long Position {
            get {
                return stream.Position + bufferOffset;
            }
            set {
                stream.Position = value;
                bufferedBytes = 0;
                bufferOffset = 0;
            }
        }

        public BufferedBinaryReader(Stream stream, int bufferSize) {
            this.stream = stream;
            this.bufferSize = bufferSize;
            buffer = new byte[bufferSize];
            bufferOffset = 0;
            bufferedBytes = 0;
        }

        public void FillBuffer(int byteCount) {
            int unreadBytes = bufferedBytes - bufferOffset;

            if (unreadBytes < byteCount) {
                if (unreadBytes != 0)
                    System.Buffer.BlockCopy(buffer, bufferOffset, buffer, 0, unreadBytes);
                bufferedBytes = stream.Read(buffer, unreadBytes, bufferSize - unreadBytes) + unreadBytes;
                bufferOffset = 0;
            }
        }

        public byte ReadByte() {
            FillBuffer(1);
            return buffer[bufferOffset++];
        }

        public sbyte ReadSByte() {
            FillBuffer(1);
            return (sbyte)buffer[bufferOffset++];
        }

        public ushort ReadUInt16() {
            FillBuffer(sizeof(ushort));
            return bit2Converter.Read(buffer, ref bufferOffset).@ushort;
        }

        public short ReadInt16() {
            FillBuffer(sizeof(short));
            return bit2Converter.Read(buffer, ref bufferOffset).@short;
        }

        public uint ReadUInt32() {
            FillBuffer(sizeof(uint));
            return bit4Converter.Read(buffer, ref bufferOffset).@uint;
        }

        public int ReadInt32() {
            FillBuffer(sizeof(int));
            return bit4Converter.Read(buffer, ref bufferOffset).@int;
        }

        public float ReadSingle() {
            FillBuffer(sizeof(float));
            return bit4Converter.Read(buffer, ref bufferOffset).@float;
        }

        public void Skip(int bytes) {
            FillBuffer(bytes);
            bufferOffset += bytes;
        }

        [StructLayout(LayoutKind.Explicit)]
        public struct Bit2Converter {
            [FieldOffset(0)] public byte b0;
            [FieldOffset(1)] public byte b1;
            [FieldOffset(0)] public short @short;
            [FieldOffset(0)] public ushort @ushort;

            [MethodImpl(MethodImplOptions.AggressiveInlining)]
            public Bit2Converter Read(byte[] buffer, ref int bufferOffset) {
                b0 = buffer[bufferOffset++];
                b1 = buffer[bufferOffset++];
                return this;
            }
        }

        [StructLayout(LayoutKind.Explicit)]
        public struct Bit4Converter {
            [FieldOffset(0)] public byte b0;
            [FieldOffset(1)] public byte b1;
            [FieldOffset(2)] public byte b2;
            [FieldOffset(3)] public byte b3;
            [FieldOffset(0)] public float @float;
            [FieldOffset(0)] public int @int;
            [FieldOffset(0)] public uint @uint;

            [MethodImpl(MethodImplOptions.AggressiveInlining)]
            public Bit4Converter Read(byte[] buffer, ref int bufferOffset) {
                b0 = buffer[bufferOffset++];
                b1 = buffer[bufferOffset++];
                b2 = buffer[bufferOffset++];
                b3 = buffer[bufferOffset++];
                return this;
            }
        }

        public void Dispose() {
            stream.Close();
        }
    }
}