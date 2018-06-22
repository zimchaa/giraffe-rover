var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _defineProperty(obj, key, value) { if (key in obj) { Object.defineProperty(obj, key, { value: value, enumerable: true, configurable: true, writable: true }); } else { obj[key] = value; } return obj; }

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var CLICKED_ITEMS = [{
  component: "",
  feature: ""
}, {
  component: "",
  action: ""
}];

var LINKS = [{
  colorIndex: "graph-2",
  ids: ["light-switch", "light-off"],
  component: "light",
  feature: "switch"
}, {
  colorIndex: "graph-2",
  ids: ["arm-grip", "arm-stop"],
  component: "arm",
  feature: "grip"
}, {
  colorIndex: "graph-2",
  ids: ["arm-wrist", "arm-stop"],
  component: "arm",
  feature: "wrist"
}, {
  colorIndex: "graph-2",
  ids: ["arm-elbow", "arm-stop"],
  component: "arm",
  feature: "elbow"
}, {
  colorIndex: "graph-2",
  ids: ["tracks-both", "tracks-stop"],
  component: "tracks",
  feature: "both"
}];

var ROBOARM = {
  description: "Giraffe Rover",
  identification: {
    description: "These are the parameters used to identify the RoboArm using the USB connection",
    idVendor: 0x1267,
    idProduct: 0x000
  },
  initialisation: {
    description: "These variables are used to transfer data on the created USB connection",
    bmRequestType: 0x40,
    bmRequest: 6,
    wValue: 0x100,
    wIndex: 0
  },
  components: {
    tracks: {
      description: "The <ARM> components are mounted on this rotating base, with approx. 270deg freedom, clockwise and counterclockwise rotation is considered from the top of the RoboArm",
      mask: 255,
      features: {
        both: {
          mask: 3,
          actions: {
            forward: 1,
            stop: 2,
            reverse: 0,
            turncw: 0,
            turnccw: 0
          }
        }
      }
    },
    arm: {
      description: "This component is mounted on the <TRACKS>, and replicates a typical human arm - with features, i.e. shoulder (unplugged), elbow, wrist and a gripper.",
      mask: 255,
      features: {
        all: {
          description: "This is a pseudo-feature that allows for complex functions to be predescribed for the whole <ARM> component",
          mask: 255,
          type: "virtual",
          actions: {
            open: 170,
            close: 85,
            stop: 0
          }
        },
        elbow: {
          description: "",
          mask: 48,
          actions: {
            open: 16,
            close: 32,
            stop: 0
          }
        },
        wrist: {
          description: "",
          mask: 12,
          actions: {
            open: 4,
            close: 8,
            lift: 4,
            stop: 0
          }
        },
        grip: {
          description: "",
          mask: 3,
          actions: {
            open: 1,
            close: 2,
            grab: 2,
            drop: 1,
            stop: 0,
            pause: 0
          }
        }
      }
    },
    light: {
      description: "This is an LED mounted behind the <GRIP> feature on the <ARM> component - the focus of the light is useful to highlight where to grab, or that the system is in use",
      mask: 255,
      features: {
        switch: {
          description: "The only feature of the <LIGHT> is the <SWITCH>, simply flipping the last bit of the 3rd byte",
          mask: 1,
          actions: {
            on: 1,
            off: 0
          }
        }
      }
    }
  }
};

var RoboArmComponents = function (_React$Component) {
  _inherits(RoboArmComponents, _React$Component);

  function RoboArmComponents() {
    _classCallCheck(this, RoboArmComponents);

    return _possibleConstructorReturn(this, (RoboArmComponents.__proto__ || Object.getPrototypeOf(RoboArmComponents)).apply(this, arguments));
  }

  _createClass(RoboArmComponents, [{
    key: "render",
    value: function render() {
      var _this2 = this;

      var componentKeys = Object.keys(this.props.componentConfig);
      var componentParts = componentKeys.map(function (componentName) {
        return React.createElement(
          Topology.Part,
          {
            a11yTitle: componentName,
            className: "component",
            key: componentName,
            direction: "row"
          },
          React.createElement(RoboArmComponentFeatures, {
            featureConfig: _this2.props.componentConfig[componentName].features,
            componentName: componentName,
            onClickItem: _this2.props.onClickItem
          }),
          React.createElement(
            Topology.Label,
            { className: "raa_component_label" },
            componentName.toUpperCase()
          ),
          React.createElement(RoboArmControlFeatures, {
            featureConfig: _this2.props.componentConfig[componentName].features,
            controlName: componentName,
            onClickItem: _this2.props.onClickItem
          })
        );
      });
      return React.createElement(
        Topology.Part,
        {
          a11yTitle: "RoboArm Component Structure",
          className: "RoboArmComponents",
          direction: "column",
          label: this.props.roboArmName
        },
        React.createElement(
          Topology.Part,
          _defineProperty({
            a11yTitle: "RoboArm Component Structure",
            className: "RoboArmComponents",
            direction: "column",
            reverse: true
          }, "className", "raa_structure"),
          componentParts
        )
      );
    }
  }]);

  return RoboArmComponents;
}(React.Component);

var RoboArmComponentFeatures = function (_React$Component2) {
  _inherits(RoboArmComponentFeatures, _React$Component2);

  function RoboArmComponentFeatures() {
    _classCallCheck(this, RoboArmComponentFeatures);

    return _possibleConstructorReturn(this, (RoboArmComponentFeatures.__proto__ || Object.getPrototypeOf(RoboArmComponentFeatures)).apply(this, arguments));
  }

  _createClass(RoboArmComponentFeatures, [{
    key: "render",
    value: function render() {
      var _this4 = this;

      // const featureRemove = "all";
      var componentName = this.props.componentName;
      var featureKeys = Object.keys(this.props.featureConfig);
      /* let displayFeatureKeys = featureKeys.filter(
        feature => feature.indexOf(featureRemove) < 0
      ); */
      var featureParts = featureKeys.map(function (featureName) {
        return React.createElement(Topology.Part, {
          id: componentName + "-" + featureName,
          status: "ok",
          label: featureName,
          direction: "row",
          demarcate: false,
          justify: "start",
          align: "center",
          key: featureName,
          className: "raa_feature",
          reverse: true,
          onClick: _this4.props.onClickItem,
          "data-id": componentName + "-" + featureName,
          "data-type": "componentFeature"
        });
      });
      return React.createElement(
        Topology.Parts,
        { direction: "column", uniform: true },
        featureParts
      );
    }
  }]);

  return RoboArmComponentFeatures;
}(React.Component);

var RoboArmControlFeatures = function (_React$Component3) {
  _inherits(RoboArmControlFeatures, _React$Component3);

  function RoboArmControlFeatures() {
    _classCallCheck(this, RoboArmControlFeatures);

    return _possibleConstructorReturn(this, (RoboArmControlFeatures.__proto__ || Object.getPrototypeOf(RoboArmControlFeatures)).apply(this, arguments));
  }

  _createClass(RoboArmControlFeatures, [{
    key: "render",
    value: function render() {
      var _this6 = this;

      var featureDisplay = "all";
      var featureKeys = Object.keys(this.props.featureConfig);
      // console.log(featureKeys.length == 1);
      var displayFeatureKeys = [];
      if (featureKeys.length == 1) {
        displayFeatureKeys = featureKeys;
      } else {
        displayFeatureKeys = featureKeys.filter(function (feature) {
          return feature.indexOf(featureDisplay) > -1;
        });
      }
      // console.log(displayFeatureKeys);
      var featureParts = displayFeatureKeys.map(function (featureName) {
        return React.createElement(
          Topology.Part,
          {
            id: featureName,
            direction: "column",
            demarcate: false,
            justify: "start",
            align: "start",
            key: featureName
          },
          React.createElement(RoboArmControlFeatureActions, {
            actionConfig: _this6.props.featureConfig[featureName].actions,
            featureName: featureName,
            controlName: _this6.props.controlName,
            onClickItem: _this6.props.onClickItem
          })
        );
      });
      return React.createElement(
        Topology.Parts,
        { direction: "column", uniform: true },
        featureParts
      );
    }
  }]);

  return RoboArmControlFeatures;
}(React.Component);

var RoboArmControlFeatureActions = function (_React$Component4) {
  _inherits(RoboArmControlFeatureActions, _React$Component4);

  function RoboArmControlFeatureActions() {
    _classCallCheck(this, RoboArmControlFeatureActions);

    return _possibleConstructorReturn(this, (RoboArmControlFeatureActions.__proto__ || Object.getPrototypeOf(RoboArmControlFeatureActions)).apply(this, arguments));
  }

  _createClass(RoboArmControlFeatureActions, [{
    key: "render",
    value: function render() {
      var _this8 = this;

      var featureName = this.props.featureName;
      var controlName = this.props.controlName;
      var actionKeys = Object.keys(this.props.actionConfig);
      var actionParts = actionKeys.map(function (actionName) {
        return React.createElement(Topology.Part, {
          id: controlName + "-" + actionName,
          status: "ok",
          label: actionName,
          direction: "row",
          demarcate: false,
          justify: "start",
          align: "center",
          key: featureName + "-" + actionName,
          className: "raa_action",
          onClick: _this8.props.onClickItem,
          "data-id": controlName + "-" + actionName,
          "data-type": "componentAction"
        });
      });
      return React.createElement(
        Topology.Parts,
        { direction: "column", uniform: true },
        actionParts
      );
    }
  }]);

  return RoboArmControlFeatureActions;
}(React.Component);

var RoboArmApp = function (_React$Component5) {
  _inherits(RoboArmApp, _React$Component5);

  function RoboArmApp(props) {
    _classCallCheck(this, RoboArmApp);

    var _this9 = _possibleConstructorReturn(this, (RoboArmApp.__proto__ || Object.getPrototypeOf(RoboArmApp)).call(this, props));

    _this9.handle_mode_switch = function (event) {
      console.log(event.target.value);
    };

    _this9.command_click = function (event) {
      var clicked_componentfeature = void 0,
          clicked_componentaction = void 0,
          cl_parts = void 0,
          cl_links = void 0;

      cl_parts = _this9.state.clicked_items;

      console.log("INFO: clicked element target data-type: " + event.currentTarget.dataset.type);
      console.log("INFO: clicked element target data-id: " + event.currentTarget.dataset.id);

      if (event.currentTarget.dataset.type == "componentFeature") {
        clicked_componentfeature = event.currentTarget.dataset.id.split("-");
        cl_parts[0].component = clicked_componentfeature[0];
        cl_parts[0].feature = clicked_componentfeature[1];
        console.log("INFO: clicked a feature: " + cl_parts[0].feature);
      } else if (event.currentTarget.dataset.type == "componentAction") {
        clicked_componentaction = event.currentTarget.dataset.id.split("-");
        cl_parts[1].component = clicked_componentaction[0];
        cl_parts[1].action = clicked_componentaction[1];
        console.log("INFO: clicked an action: " + cl_parts[1].action);
      } else {
        console.log("ERROR: something wasn't clicked right?");
      }

      if (cl_parts[0].component == cl_parts[1].component && cl_parts[0].component != "") {
        _this9.update_links(cl_parts[0].component, cl_parts[0].feature, cl_parts[1].action);

        cl_parts[1].component = "";
        // this stops the last clicked action from becoming the action for the next component
      }

      _this9.setState({
        clicked_items: cl_parts
      });
    };

    _this9.state = {
      move_command: { arm: 0, base: 0, light: 0 },
      clicked_items: CLICKED_ITEMS,
      command_links: LINKS
    };
    return _this9;
  }

  _createClass(RoboArmApp, [{
    key: "update_links",
    value: function update_links(component, feature, action) {
      var updated_link = false;
      var curr_links = this.state.command_links;

      for (var i = 0; i < curr_links.length; i++) {
        // console.log("checking: " + i);
        // console.log("component: " + curr_links[i].component);
        // console.log("feature: " + curr_links[i].feature);
        if (curr_links[i].component == component && curr_links[i].feature == feature) {
          curr_links[i].ids = [component + "-" + feature, component + "-" + action];
          updated_link = true;
          // console.log("updating: " + i);
        }
      }
      if (!updated_link) {
        curr_links.push({
          colorIndex: "graph-3",
          ids: [component + "-" + feature, component + "-" + action],
          component: component,
          feature: feature
        });
      }

      this.setState({
        command_links: curr_links
      });

      this.invoke_api(component, feature, action);
    }
  }, {
    key: "invoke_api",
    value: function invoke_api(component, feature, action) {
      var api_url = window.location.protocol + "//" + window.location.hostname + ":" + window.location.port;
      var api_path = "/roboarm/" + component + "/" + feature + "/" + action;

      console.log(api_url + api_path);

      var raa = this;

      fetch(api_url + api_path).then(function (resp) {
        return resp.json();
      }).then(function (data) {
        raa.update_move_command(data);
        console.log("INFO: updated move command: " + data);
      }).catch(function (error) {
        console.log("ERROR: " + error);
      });
    }
  }, {
    key: "update_move_command",
    value: function update_move_command(move_command_response) {
      this.setState({
        move_command: move_command_response
      });
    }
  }, {
    key: "render",
    value: function render() {
      var _React$createElement2;

      return React.createElement(
        App,
        null,
        React.createElement(
          Box,
          (_React$createElement2 = {
            align: "center",
            pad: "medium",
            colorIndex: "neutral-1",
            margin: "medium"
          }, _defineProperty(_React$createElement2, "pad", "small"), _defineProperty(_React$createElement2, "direction", "column"), _React$createElement2),
          React.createElement(
            Box,
            { margin: "medium" },
            React.createElement(CheckBox, {
              label: "Live Mode",
              id: "mode_switch",
              name: "mode_switch",
              defaultChecked: true,
              onChange: this.handle_mode_switch,
              disabled: true
            })
          ),
          React.createElement(
            Box,
            { margin: "medium" },
            React.createElement("img", {
              src: window.location.protocol + "//" + window.location.hostname + "/html/cam_pic_new.php",
              alt: "Live Feed"
            })
          ),
          React.createElement(
            Box,
            { margin: "medium" },
            React.createElement(
              Topology,
              {
                a11yTitle: this.props.roboarmConfig.description,
                links: this.state.command_links
              },
              React.createElement(
                Topology.Parts,
                { direction: "column", uniform: true },
                React.createElement(
                  Topology.Part,
                  { direction: "column" },
                  React.createElement(RoboArmComponents, {
                    componentConfig: this.props.roboarmConfig.components,
                    roboArmName: this.props.roboarmConfig.description,
                    onClickItem: this.command_click
                  })
                )
              )
            )
          )
        )
      );
    }
  }]);

  return RoboArmApp;
}(React.Component);

var element = document.getElementById("content");
ReactDOM.render(React.createElement(RoboArmApp, { roboarmConfig: ROBOARM }), element);