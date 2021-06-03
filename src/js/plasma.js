const floor3D = (i) => [ Math.floor(i[0]), Math.floor(i[1]), Math.floor(i[2]) ];
const add3D = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
const sub3D = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];

const mix   = (a, b, weight) => a*(1.0-weight) + b*weight;
const mix3D = (a, b, weight) => [
    mix(a[0], b[0], weight),
    mix(a[1], b[1], weight),
    mix(a[2], b[2], weight)
];

function gradient3D(i) {
    var rand = 2920.0
        * Math.sin(i[0]*21942.0 + i[1]*171324.0 + i[2]*940957.0 + 8912.0)
        * Math.cos(i[0]*23157.0 + i[1]*217832.0 + i[2]*298391.0 + 9758.0);

    return [ Math.cos(rand), Math.sin(rand), Math.cos(-15017.0*rand) ];
}

function dotGradient3D(i, pos) {
    var grad = gradient3D(i);
    var dist = sub3D(pos, i);

    return dist[0]*grad[0] + dist[1]*grad[1] + dist[2]*grad[2];
}

function perlin(pos) {
    var grid = [
        floor3D(pos),
        floor3D(add3D(pos, [1.0, 1.0, 1.0]))
    ];

    var weight = sub3D(pos, grid[0]);
    var n = Array(8);

    for (var i = 0; i < 8; i++) {
        var x = [
            grid[!!(i&1)?1:0][0],
            grid[!!(i&2)?1:0][1],
            grid[!!(i&4)?1:0][2]
        ];
        n[i] = dotGradient3D(x, pos);
    }

    var ix0 = mix(n[0], n[1], weight[0]);
    var ix1 = mix(n[2], n[3], weight[0]);
    var ix2 = mix(n[4], n[5], weight[0]);
    var ix3 = mix(n[6], n[7], weight[0]);

    var iy0 = mix(ix0, ix1, weight[1]);
    var iy1 = mix(ix2, ix3, weight[1]);

    return Math.max(0.0, mix(iy0, iy1, weight[2]));
}

var chars = [
    ' ',
    ':',
    ':',
    '-',
    '=',
    '=',
    '+',
    '+',
    'o',
    '{',
    '}',
    '▓',
    '█',
    '█',
];

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

function pattern(width, height) {
    for (var z = 0; z < 1000; z++) {
        grid = Array(width);
        for (var i = 0; i < width; i++) {
            grid[i] = Array(height);
            for (var k = 0; k < height; k++) {
                grid[i][k] = 0;
            }
        }

        for (var y = 0; y < height; y++) {
            for (var x = 0; x < width; x++) {
                var amt = perlin([x*0.1, y*0.1, z*0.1]);
                grid[i][k] = amt;
            }
        }
    }
}

var asdf = "Stay tuned...";

function makePatternAnim(em, width, height) {
    let start;
    return (timestamp) => {
        if (start === undefined) {
            start = timestamp;
        }

        var step = timestamp - start;
        var built = "";

        for (var y = 0; y < height; y++) {
            for (var x = 0; x < width; x++) {
                var amt = perlin([x*0.1, y*0.1, step*0.0005]);
                var offset = 7;

                if (y == 15 && x >= offset && x - offset < asdf.length) {
                    built += asdf[x-offset];

                } else {
                    let len = chars.length;
                    built += chars[Math.min(len, Math.floor(amt*len))];
                }
            }
            built += "\n";
        }

        em.value = built;
    }
}

function doAnim(f) {
    return (timestamp) => {
        f(timestamp);
        window.requestAnimationFrame(doAnim(f));
    }
}

//pattern(48, 24);
var foo = document.getElementById("plasmaArea");
window.requestAnimationFrame(doAnim(makePatternAnim(foo, 36, 18)));
