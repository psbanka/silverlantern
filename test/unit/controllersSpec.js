'use strict';

describe('SilverLining controllers', function() {

  describe('galleryCtrl', function(){

    var scope, ctrl, $httpBackend;

    beforeEach(inject(function(_$httpBackend_, $rootScope, $controller) {
        $httpBackend = _$httpBackend_;
        $httpBackend.expectGET('/json/gallery_words/').
          respond([
            {
                "category": "hipster",
                "words": [
                    {'word': 'abhorrent', 'info': "hello kitty"},
                    {'word': 'abrasive', 'info': "hello kitty"},
                    {'word': 'alluring', 'info': "hello kitty"},
                    {'word': 'ambiguous', 'info': "hello kitty"},
                    {'word': 'apathetic', 'info': "hello kitty"},
                    {'word': 'amuck', 'info': "hello kitty"}
                ]
            },
            {
                "category": "charming",
                "words": [
                    {'word': 'darling', 'info': "hello kitty"},
                    {'word': 'magical', 'info': "hello kitty"},
                    {'word': 'effervescent', 'info': "hello kitty"}
                ]
            }
        ]);
        scope = $rootScope.$new();
        ctrl = $controller(galleryCtrl, {$scope: scope});
    }));

    it('should create "pageSize" model equal to 4', function() {
      expect(scope.pageSize).toBe(4);
    });

    it('should create a list of two categories', function() {
      $httpBackend.flush();
      expect(scope.categories.length).toBe(2);
    });

    it('should create six words', function() {
      $httpBackend.flush();
      expect(scope.words.length).toBe(6);
    });

    it('should change to three words when selecting another category', function() {
      $httpBackend.flush();
      scope.setCategory("charming");
      expect(scope.words.length).toBe(3);
    });

    it('should be able to change the category selected', function() {
      $httpBackend.flush();
      expect(scope.isSelected("charming")).toBe(false);
      expect(scope.isSelected("hipster")).toBe(true);
      scope.setCategory("charming");
      expect(scope.isSelected("charming")).toBe(true);
      expect(scope.words.length).toBe(3);
    });

    it('should populate wordData', function() {
      $httpBackend.flush();
      expect(scope.wordData['charming'][0]['word']).toBe('darling');
    });

  });
});

