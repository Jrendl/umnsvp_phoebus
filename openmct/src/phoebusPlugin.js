// import openmct from "openmct";
import {_} from "lodash";
import { io } from "socket.io-client";
// Pho
function PhoebusObjectProvider(identifier) {
    // console.log("obj provider", identifier)
    const board_regex = /^board\.([a-z-_]+)$/
    const packet_regex = /^board\.([a-z-_]+)\.([a-z-_]+)$/
    const data_field_regex = /^board\.([a-z-_]+)\.([a-z-_]+)\.([a-z-_]+)$/ // board.wavesculptor.wsl_heatsink_motor_temp.motor_temp
    const data_field_regex_num = /^board\.([a-z-_]+)\.([a-z-_]+)\.([A-Za-z0-9]+)$/ // board.car_control.dashboard_system_timeout_test.flag_set0
    const packet_regex_underscore_num = /^board\.([a-z-_]+)\.([a-z-_]+(_[A-Za-z0-9]+)+)$/ // board.steering.steering_press_count_1
    const data_field_regex_underscore_num1 = /^board\.([a-z-_]+)\.([a-z-_]+(_[A-Za-z0-9]+)+)\.([A-Za-z0-9]+)$/ // board.steering.steering_press_count_1.button1
    const data_field_regex_underscore_num2 = /^board\.([a-z-_]+)\.([a-z-_]+)\.([a-z-_]+(_[A-Za-z0-9]+)+)$/ // board.wavesculptor.wsr_status_information.error_flags_0
    const data_field_regex_underscore_num3 = /^board\.([a-z-_]+)\.([a-z-_]+(_[A-Za-z0-9]+)+)\.([A-Za-z0-9]+(_[A-Za-z0-9]+)+)$/ // board.wavesculptor.wsr_15_165_voltage_rail.reference_165v
    if (identifier.key === 'car') {
        // get the car schema from the phoebus server
        return Promise.resolve({
            identifier: identifier,
            name: "car!",
            type: 'folder',
            location: "ROOT"
        })
    } else if (board_regex.test(identifier.key)) {
        // it's a board object. get the last word (ie board.bms -> bms)
        // then use it to construct a get request
        // console.log("doing board for ", identifier)
        const board_name = identifier.key.match(board_regex)[1]
        return fetch(`${process.env.VUE_APP_TELEM}/schema/` + board_name).then((resp) => {
            return resp.json()
        })
    } else if (packet_regex.test(identifier.key)) {
        const m = identifier.key.match(packet_regex)
        const board_name = m[1]
        const pkt_name = m[2]
        return fetch([`${process.env.VUE_APP_TELEM}/schema`, board_name, pkt_name].join("/")).then((resp) => {
            return resp.json()
        })
    } else if (data_field_regex.test(identifier.key)) {
        const m = identifier.key.match(data_field_regex)
        const board_name = m[1]
        const pkt_name = m[2]
        const df_name = m[3]
        return fetch([`${process.env.VUE_APP_TELEM}/schema`, board_name, pkt_name, df_name].join("/")).then((resp) => {
            return resp.json();
        })
    } else if (data_field_regex_num.test(identifier.key)) {
        const m = identifier.key.match(data_field_regex_num)
        const board_name = m[1]
        const pkt_name = m[2]
        const df_name = m[3]
        return fetch([`${process.env.VUE_APP_TELEM}/schema`, board_name, pkt_name, df_name].join("/")).then((resp) => {
            return resp.json();
        })
    } else if (packet_regex_underscore_num.test(identifier.key)) {
        const m = identifier.key.match(packet_regex_underscore_num)
        const board_name = m[1]
        const pkt_name = m[2]
        return fetch([`${process.env.VUE_APP_TELEM}/schema`, board_name, pkt_name].join("/")).then((resp) => {
            return resp.json();
        })
    } else if (data_field_regex_underscore_num1.test(identifier.key)) {
        const m = identifier.key.match(data_field_regex_underscore_num1)
        const board_name = m[1]
        const pkt_name = m[2]
        const df_name = m[4]
        return fetch([`${process.env.VUE_APP_TELEM}/schema`, board_name, pkt_name, df_name].join("/")).then((resp) => {
            return resp.json();
        })
    } else if (data_field_regex_underscore_num2.test(identifier.key)) {
        const m = identifier.key.match(data_field_regex_underscore_num2)
        const board_name = m[1]
        const pkt_name = m[2]
        const df_name = m[3]
        return fetch([`${process.env.VUE_APP_TELEM}/schema`, board_name, pkt_name, df_name].join("/")).then((resp) => {
            return resp.json();
        })
    } else if (data_field_regex_underscore_num3.test(identifier.key)) {
        const m = identifier.key.match(data_field_regex_underscore_num3)
        const board_name = m[1]
        const pkt_name = m[2]
        const df_name = m[4]
        return fetch([`${process.env.VUE_APP_TELEM}/schema`, board_name, pkt_name, df_name].join("/")).then((resp) => {
            return resp.json();
        })
    }

    console.error("bad! no match for object.")
    return {}
}

function getSchema() {
    return fetch(`${process.env.VUE_APP_TELEM}/schema`).then((resp) => {
        const res = resp.json()
        console.log("got schema", res)
        return res
    })
}

const CarCompositionProvider = {
    appliesTo: function (domainObject) {
        return domainObject.identifier.namespace === "umnsvp.phoebus" &&
            domainObject.identifier.key === "car"
    },
    load: function (domainObject) {
        return getSchema()
    }
}

// the board composition provider takes a board type object, and gets all the telem objects for that board.
// it's like a folder.
const BoardCompositionProvider = {
    appliesTo: function (domainObject) {
        return domainObject.identifier.namespace === "umnsvp.phoebus" &&
            domainObject.type === "umnsvp-board"
    },
    load: function (domainObject) {
        // console.log("board comp provider for ", domainObject.packets)
        return Promise.resolve(domainObject.packets)
        // const board_name = domainObject.identifier.key.match(/^board\.([a-z-_]+)$/)
        // return fetch("${process.env.VUE_APP_TELEM}/schema/" + board_name[1] + "/packets").then((resp) => {
        //     return resp.json()
        // })
    }
}

const PacketCompositionProvider = {
    appliesTo: function (domainObject) {
        return domainObject.identifier.namespace === "umnsvp.phoebus" && domainObject.type === "umnsvp-packet"
    },
    load: function (domainObject) {
        // console.log("packet comp provider for ", domainObject.data_fields)
        return Promise.resolve(domainObject.data_fields)
    }
}

const PhoebusCompositionProviders = [
    CarCompositionProvider,
    BoardCompositionProvider,
    PacketCompositionProvider
]


function PhoebusRealTime() {
    const socket = io(`ws://localhost:${process.env.VUE_APP_TELEM_PORT}`)
    let callback_list = {};
    socket.on("packet", (data) => {
        // if (data[0].packet_name === "wsl_bus_measurement") {
        //     console.log("got a wave meas packt", data[0])
        // }
        try {
            const data_fields = data[0].data[0] // object that defines the measurement in each packet which are sent to openmct
            // const key = ["board", data[0].board, data[0].packet_name].join(".")
            console.log(Object.keys(data_fields))
            console.log(callback_list)
            // for (let i = 0; i < callback_list.length; i++) {
            //     if (Object.keys(data_fields).includes())
            // }
            Object.keys(data_fields).forEach((data_field) => {
                let key = ["board", data[0].board, data[0].packet_name, data_field].join(".");
                if (Object.keys(callback_list).includes(key)) {
                    let callBack = callback_list[key];
                    let timestamp = new Date().getTime();
                    // let realTimeData = data_fields;
                    let realTimeData = {}
                    realTimeData[data_field] = data_fields[data_field]
                    realTimeData.timestamp = timestamp;
                    realTimeData.id = key;
                    // console.log(realTimeData)
                    callBack(realTimeData);
                }
            })
        } catch (e) {
            // do nothing
            console.warn("a", e)
        }
    })

    const provider = {
        supportsSubscribe(domainObject) {
            console.log("checking if supports subscribe", domainObject)
            return domainObject.type === "umnsvp-data"
        },
        subscribe(domainObject, callback) {
            console.log("subscribing for ", domainObject)
            console.log("callback", callback)
           // register us in the callback list
           callback_list[domainObject.identifier.key] = callback
           return function unsubscribe() {
               delete callback_list[domainObject.identifier.key]
           }
        }
    }
    return provider;
}

function PhoebusHistorical() {
    return {
        supportsRequest(domainObject) {
            return domainObject.type === "umnsvp-packet"
        },
        request(domainObject, options) {
            // return fetch()
        }
    }
}

function PhoebusPlugin() {
    return function install(openmct) {
        openmct.types.addType('umnsvp-board', {
            name: "UMN SVP Board",
            description: 'A board that sends telemetry packets/data',
            createable: false,
            cssClass: "icon-suitcase"
        })
        openmct.types.addType('umnsvp-packet', {
            name: "UMN SVP Packet",
            description: "A packet of telemetry from the car",
            creatable: false,
            cssClass: "icon-suitcase"
        })
        openmct.types.addType('umnsvp-data', {
            name: "UMN SVP Data Field",
            description: "A data field of a packet from the car",
            creatable: false,
            cssClass: "icon-telemetry"
        })
        openmct.objects.addRoot({
            namespace: "umnsvp.phoebus",
            key: 'car'
        })

        openmct.objects.addProvider('umnsvp.phoebus', {get:PhoebusObjectProvider})

        openmct.telemetry.addProvider(PhoebusRealTime())
        PhoebusCompositionProviders.forEach((provider) => {
            openmct.composition.addProvider((provider))
        })

        console.log("hello~!")
    }
}

export default PhoebusPlugin;