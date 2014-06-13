'use strict';
var m2mApp = angular.module('m2mApp', ['restangular', 'ngRoute', 'angularMoment', 'ui.bootstrap']);

m2mApp.constant('API_BASE_URL', 'http://172.19.58.159/api/v1/')

m2mApp.config(['$routeProvider', '$locationProvider', 'RestangularProvider', 'API_BASE_URL',
    function($routeProvider, $locationProvider, RestangularProvider, API_BASE_URL) {

        $routeProvider.when("/", {
            templateUrl: "/views/devicetypes.html",
            controller: 'DeviceTypesController',
            title: "Device Types"
        })
            .when("/newdevicetype", {
                templateUrl: "/views/newdevicetype.html",
                controller: 'NewDeviceType',
                title: "New Device Type"
            })
            .when("/:type_id", {
                templateUrl: "/views/devicetype.html",
                controller: 'DeviceTypeController',
                title: "Device Type"
            })
            .when("/:type_id/newdevices", {
                templateUrl: "/views/newdevices.html",
                controller: 'NewDevicesControllers',
                title: "Add Devices"
            })
            .when("/:type_id/devices/:serial_number", {
                templateUrl: "/views/device.html",
                controller: "DeviceController",
                title: "Device"
            })
            .otherwise({
                redirectTo: "/"
            });

        $locationProvider.html5Mode(true);

        RestangularProvider.setBaseUrl(API_BASE_URL);
        RestangularProvider.setDefaultHeaders({
            'Content-Type': 'application/json'
        });

    }
]);

m2mApp.run(['$rootScope',
    function($rootScope) {
        $rootScope.$on('$routeChangeSuccess', function(event, current, previous) {
            $rootScope.pageTitle = current.title;
        });
    }
]);

m2mApp.controller('DeviceTypesController', ['$scope', 'Restangular','$http','API_BASE_URL',
    function($scope, Restangular, $http, API_BASE_URL) {
        Restangular.all('devicetypes').getList().then(function(devicetypes) {
            $scope.types = devicetypes
        }, function() {
            console.log("ERROR");
        });

        $scope.delete = function(devicetype) {
             $http({
                method: 'DELETE',
                url: API_BASE_URL + "devicetypes/" + devicetype.id
            }).success(function(data, status, headers, config) {
                $scope.types = _.without($scope.types, devicetype)
            }).error(function(data, status, headers, config) {
                console.log("ERROR", data, status, headers, config)
            });
        }
    }
]);

m2mApp.controller('NewDeviceType', ['$scope', '$location', 'Restangular', '$window',
    function($scope, $location, Restangular, $window) {
        $scope.submit = function() {
            Restangular.all('devicetypes').post($scope.device).then(function() {
                $location.path("/")
            }, function() {
                console.log("ERROR!!!!")
            });
        };

        $scope.back = function() {
            $window.history.back();
        }
    }
]);

m2mApp.controller('DeviceTypeController', ['$scope', '$routeParams', 'Restangular', '$http', 'API_BASE_URL',
    function($scope, $routeParams, Restangular, $http, API_BASE_URL) {
        Restangular.one("devicetypes", $routeParams.type_id).get().then(function(response) {
            $scope.deviceType = response.device_type_metadata;
            $scope.deviceType.tags = ["Tag1"];
            $scope.devices = response.devices;
        }, function(error) {
            console.log(error.status);
        });

        $scope.deleteDevice = function(device) {
            // console.log("http://192.168.1.125/api/v1/devicetypes/" + $scope.deviceType.id + "/devices/" + device.serial_number)
            $http({
                method: 'DELETE',
                url: API_BASE_URL + "devicetypes/" + $scope.deviceType.id + "/devices/" + device.serial_number
            }).success(function(data, status, headers, config) {
                $scope.devices = _.without($scope.devices, device)
            }).error(function(data, status, headers, config) {
                console.log("ERROR", data, status, headers, config)
            });
        }
    }
]);

m2mApp.controller('NewDevicesControllers', ['$scope', '$routeParams', '$http', '$window', 'API_BASE_URL', '$location',
    function($scope, $routeParams, $http, $window, API_BASE_URL, $location) {

        $scope.back = function() {
            $window.history.back();
        }

        $scope.submit = function() {
            $http({
                method: 'POST',
                url: API_BASE_URL + "devicetypes/" + $routeParams.type_id + "/devices",
                headers: {
                    "Content-Type": "text/plain"
                },
                data: $scope.newDevices
            }).success(function(data, status, headers, config) {
                $location.path("/" + $routeParams.type_id)
            }).error(function(data, status, headers, config) {
                console.log("ERROR", data, status, headers, config)
            })

        }

    }
]);

m2mApp.controller('DeviceController', ['$scope', '$routeParams','Restangular',
    function($scope, $routeParams, Restangular) {
        Restangular.one("devicetypes", $routeParams.type_id).one('devices', $routeParams.serial_number).get().then(function(result){
            console.log(result.device);
            $scope.device = result.device;
        })
    }
]);
