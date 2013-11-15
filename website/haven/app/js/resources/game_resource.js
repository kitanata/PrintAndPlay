angular.module("app").factory("GameResource", function($q, $resource) {
  return $resource('/api/games');
});
