# Static province-based map preview. Does not start CK3 or require Python imaging packages.
$ErrorActionPreference='Stop'
$Root='C:\antiquity_359_bc'
Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.IO.Compression.FileSystem
$Code=@'
using System;
using System.IO;
using System.IO.Compression;
using System.Drawing;
using System.Drawing.Imaging;
using System.Drawing.Drawing2D;
using System.Runtime.InteropServices;
using System.Collections.Generic;
public static class Antiquity040Map {
 public static void Render(string archive, string dir) {
  int[] palette=new int[16777216]; ushort[] owner=new ushort[16777216];
  int water=Color.FromArgb(154,180,202).ToArgb();
  for(int i=0;i<palette.Length;i++)palette[i]=water;
  foreach(string line in File.ReadAllLines(Path.Combine(dir,"province_preview_lookup.csv"))) {
   string[] p=line.Split(';');if(p.Length<3)continue;
   int rgb=int.Parse(p[0]);palette[rgb]=int.Parse(p[1]);owner[rgb]=ushort.Parse(p[2]);
  }
  Dictionary<int,string> labels=new Dictionary<int,string>();
  foreach(string line in File.ReadAllLines(Path.Combine(dir,"preview_labels.csv"))) {
   int sep=line.IndexOf(';');if(sep>0)labels[int.Parse(line.Substring(0,sep))]=line.Substring(sep+1);
  }
  int width=2200,height; Bitmap map;
  using(ZipArchive zip=ZipFile.OpenRead(archive)) {
   ZipArchiveEntry entry=zip.GetEntry("game/map_data/provinces.png");
   if(entry==null)throw new Exception("Native province raster is missing.");
   using(Stream stream=entry.Open())using(Image image=Image.FromStream(stream))using(Bitmap src=new Bitmap(image.Width,image.Height,PixelFormat.Format24bppRgb)) {
    using(Graphics g=Graphics.FromImage(src))g.DrawImageUnscaled(image,0,0);
    height=(int)Math.Round((double)width*src.Height/src.Width);map=new Bitmap(width,height,PixelFormat.Format32bppArgb);
    BitmapData sd=src.LockBits(new Rectangle(0,0,src.Width,src.Height),ImageLockMode.ReadOnly,PixelFormat.Format24bppRgb);
    byte[] data=new byte[sd.Stride*sd.Height];Marshal.Copy(sd.Scan0,data,0,data.Length);src.UnlockBits(sd);
    int[] pixels=new int[width*height];ushort[] states=new ushort[pixels.Length];
    for(int y=0;y<height;y++)for(int x=0;x<width;x++) {
     int sx=(int)((long)x*src.Width/width),sy=(int)((long)y*src.Height/height),a=sy*sd.Stride+sx*3;
     int rgb=(data[a+2]<<16)|(data[a+1]<<8)|data[a];int i=y*width+x;
     pixels[i]=palette[rgb];states[i]=owner[rgb];
    }
    // Boundaries are rendered only between named realms, not as thousands of artificial ethnographic states.
    int[] outlined=(int[])pixels.Clone();
    for(int y=1;y<height;y++)for(int x=1;x<width;x++) {
     int i=y*width+x;
     if(states[i]!=0 && ((states[i-1]!=states[i] && pixels[i-1]!=water)||(states[i-width]!=states[i] && pixels[i-width]!=water)))
      outlined[i]=Color.FromArgb(117,127,119).ToArgb();
    }
    BitmapData md=map.LockBits(new Rectangle(0,0,width,height),ImageLockMode.WriteOnly,PixelFormat.Format32bppArgb);
    Marshal.Copy(outlined,0,md.Scan0,outlined.Length);map.UnlockBits(md);
    long[] sxsum=new long[256],sysum=new long[256],n=new long[256];
    for(int i=0;i<states.Length;i++){int k=states[i];if(k>0){sxsum[k]+=i%width;sysum[k]+=i/width;n[k]++;}}
    PointF[] centers=new PointF[256];double[] best=new double[256];for(int i=0;i<256;i++)best[i]=double.MaxValue;
    for(int i=0;i<states.Length;i++){int k=states[i];if(k==0)continue;double dx=i%width-(double)sxsum[k]/n[k],dy=i/width-(double)sysum[k]/n[k],d=dx*dx+dy*dy;if(d<best[k]){best[k]=d;centers[k]=new PointF(i%width,i/width);}}
    Draw(map,new Rectangle(0,0,width,height),width,Path.Combine(dir,"political_preview_world.png"),"359 BC | Implemented political realms",labels,centers,n,false);
    HashSet<string> china=new HashSet<string>{"Qin","Zhao","Wei","Han","Qi","Yan","Song","Chu","Zhou","Yue","Shu","Ba","Lu","Wey","Zhongshan"};
    int minx=width,miny=height,maxx=0,maxy=0;
    for(int i=0;i<states.Length;i++){int k=states[i];if(k!=0&&labels.ContainsKey(k)&&china.Contains(labels[k])){int x=i%width,y=i/width;minx=Math.Min(minx,x);maxx=Math.Max(maxx,x);miny=Math.Min(miny,y);maxy=Math.Max(maxy,y);}}
    if(maxx>minx){minx=Math.Max(0,minx-35);miny=Math.Max(0,miny-35);maxx=Math.Min(width,maxx+35);maxy=Math.Min(height,maxy+35);Draw(map,new Rectangle(minx,miny,maxx-minx,maxy-miny),1500,Path.Combine(dir,"political_preview_china.png"),"359 BC | Warring States and neighbouring realms",labels,centers,n,true);}
   }
  }
  map.Dispose();Console.WriteLine("Native-map previews written to "+dir);
 }
 static void Draw(Bitmap map,Rectangle crop,int outputWidth,string path,string title,Dictionary<int,string> labels,PointF[] centers,long[] counts,bool all) {
  int mapHeight=(int)Math.Round((double)outputWidth*crop.Height/crop.Width);float scale=(float)outputWidth/crop.Width;
  using(Bitmap dst=new Bitmap(outputWidth,mapHeight+90))using(Graphics g=Graphics.FromImage(dst))using(Font heading=new Font("Arial",19,FontStyle.Bold))using(Font label=new Font("Arial",all?12:11,FontStyle.Bold))using(Font foot=new Font("Arial",10)) {
   g.Clear(Color.White);g.InterpolationMode=InterpolationMode.NearestNeighbor;g.PixelOffsetMode=PixelOffsetMode.Half;
   g.DrawImage(map,new Rectangle(0,52,outputWidth,mapHeight),crop,GraphicsUnit.Pixel);
   g.DrawString(title,heading,Brushes.Black,20,13);
   List<RectangleF> occupied=new List<RectangleF>();
   foreach(KeyValuePair<int,string> kv in labels) {
    int k=kv.Key;if(counts[k]==0||!crop.Contains((int)centers[k].X,(int)centers[k].Y))continue;
    if(!all&&counts[k]<650&&kv.Value!="Macedon"&&kv.Value!="Rome")continue;
    float x=(centers[k].X-crop.X)*scale,y=(centers[k].Y-crop.Y)*scale+52; if(!all && kv.Value=="Macedon") { x+=28; y+=24; } SizeF size=g.MeasureString(kv.Value,label);
    RectangleF box=new RectangleF(x-size.Width/2,y-size.Height/2,size.Width,size.Height);bool collision=false;
    foreach(RectangleF prev in occupied)if(box.IntersectsWith(prev)){collision=true;break;}
    if(collision&&!all&&kv.Value!="Macedon"&&kv.Value!="Rome")continue;
    occupied.Add(box);using(SolidBrush backing=new SolidBrush(Color.FromArgb(185,255,255,255)))g.FillRectangle(backing,box);g.DrawString(kv.Value,label,Brushes.Black,box.Location);
   }
   g.DrawString("Static rendering of mod ownership on the supplied native province map. Pale areas: other chiefdoms or impassable terrain. Not an in-game screenshot.",foot,Brushes.Black,15,mapHeight+63);
   dst.Save(path,ImageFormat.Png);
  }
 }
}
'@
Add-Type -TypeDefinition $Code -ReferencedAssemblies System.Drawing,System.IO.Compression,System.IO.Compression.FileSystem
[Antiquity040Map]::Render('C:\Users\Super\Downloads\game.zip',(Join-Path $Root 'source_data\040'))
