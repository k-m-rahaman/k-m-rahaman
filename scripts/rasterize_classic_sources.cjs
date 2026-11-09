const fs=require('node:fs');
const path=require('node:path');
let sharp;
try {sharp=require('sharp');} catch(error) {
  if(!process.env.KAZI_NODE_MODULES) throw new Error('Run npm install to install sharp.');
  sharp=require(path.join(process.env.KAZI_NODE_MODULES,'sharp'));
}
const root=path.resolve(__dirname,'..');
const source=path.join(root,'assets/classic-stats-sources');
const output=source;
fs.mkdirSync(output,{recursive:true});
const recolor={'#3572A5':'#FF64C8','#555555':'#6BAAFF','#b07219':'#60E9B5','#3178c6':'#A78BFA','#e34c26':'#FFC478','#f1e05a':'#45E4FF','#012456':'#FBE58E'};
(async()=>{
for(const name of ['stats','repos-per-language','most-commit-language','productive-time','grade','profile-details','streak']){
 const raw=fs.readFileSync(path.join(source,name+'.svg'),'utf8');
 
 let svg=raw;
 for(const [a,b] of Object.entries(recolor))svg=svg.replaceAll(a,b);
 // Use the same available sans-serif family as the other source cards. Some
 // SVG rasterizers fall back to serif when Inter is unavailable in a shorthand.
 svg=svg.replaceAll("'Inter', Ubuntu, \"Helvetica Neue\", Sans-Serif", "'Segoe UI', sans-serif")
        .replaceAll("'Inter', Ubuntu, Sans-Serif", "'Segoe UI', sans-serif");
 // Snapshot animated providers in their final readable state. Streak Stats uses
 // inline opacity:0 delays, whereas Readme Stats uses the .stagger class.
 // The grade card contains nested icon SVGs: inject at the root closing tag,
 // rather than into the first icon's closing tag.
svg = svg.replace(
  /<\/svg>\s*$/,
  `<style>
    * {
      animation: none !important;
    }

    [style*="animation:"] {
      opacity: 1 !important;
      animation: none !important;
    }

    rect[data-testid="card-bg"] {
      stroke: none !important;
    }

    text {
      font-family: "Segoe UI", sans-serif !important;
    }

    .stagger {
      opacity: 1 !important;
    }

    .rank-text {
      transform: translate(-5px, 5px) scale(1) !important;
    }

    .rank-circle,
    .rank-circle-rim {
      display: none !important;
    }
  </style></svg>`
);
 const png=await sharp(Buffer.from(svg),{density:192}).png().toBuffer();
 fs.writeFileSync(path.join(output,name+'.png'),png);
 const metadata=await sharp(png).metadata();
 console.log(name,metadata.width,metadata.height);
}

})().catch(error=>{console.error(error);process.exit(1)});
