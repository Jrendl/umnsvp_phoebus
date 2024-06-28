import openmct from 'openmct';
import PhoebusPlugin from "./phoebusPlugin";
openmct.setAssetPath('node_modules/openmct/dist');
openmct.install(openmct.plugins.LocalStorage());
openmct.install(openmct.plugins.MyItems());
openmct.install(openmct.plugins.UTCTimeSystem());
openmct.time.clock('local', {start: -5 * 60 * 1000, end: 0});
openmct.time.timeSystem('utc');
openmct.install(openmct.plugins.Espresso());
openmct.install(PhoebusPlugin());

openmct.start();
